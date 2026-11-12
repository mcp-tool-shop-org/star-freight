"""Market screen — buy and sell overlay goods at the current station."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession


class TradeDialog(ModalScreen[str | None]):
    """Quantity input for a buy or sell."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, action: str, good_id: str, good_name: str, max_qty: int, price: int) -> None:
        super().__init__()
        self.action = action
        self.good_id = good_id
        self.good_name = good_name
        self.max_qty = max_qty
        self.price = price

    def compose(self) -> ComposeResult:
        total_max = self.price * self.max_qty
        with Vertical(id="input-area"):
            yield Static(
                f"[bold #f0c040]{self.action.title()} {self.good_name}[/bold #f0c040]\n\n"
                f"  Price: [yellow]{self.price}[/yellow] ₡ each\n"
                f"  Max:   [cyan]{self.max_qty}[/cyan] units"
                + (f" ([yellow]{total_max:,}[/yellow] ₡)" if self.action == "buy" else "")
            )
            yield Input(
                placeholder=f"Quantity (1-{self.max_qty})",
                id="qty-input",
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text.isdigit() and 0 < int(text) <= self.max_qty:
            self.dismiss(text)
        else:
            self.notify(f"Enter 1-{self.max_qty}", severity="warning")

    def action_cancel(self) -> None:
        self.dismiss(None)


class GoodSelectDialog(ModalScreen[str | None]):
    """Pick a good by number or name."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, action: str, goods: list[tuple[str, str, int, int]]) -> None:
        super().__init__()
        self.action = action
        self.goods = goods

    def compose(self) -> ComposeResult:
        with Vertical(id="input-area"):
            lines = [f"[bold #f0c040]{self.action.title()} which good?[/bold #f0c040]", ""]
            for i, (_gid, name, price, extra) in enumerate(self.goods, 1):
                price_str = f"[yellow]{price}[/yellow]" if price > 0 else "[dim]-[/dim]"
                extra_str = ""
                if extra > 0 and self.action == "buy":
                    extra_str = f" [dim](stock: {extra})[/dim]"
                elif extra > 0 and self.action == "sell":
                    extra_str = f" [dim](held: {extra})[/dim]"
                lines.append(f"  [cyan]{i:2d}[/cyan]. {name:16s} {price_str} ₡{extra_str}")
            lines.append("")
            yield Static("\n".join(lines))
            yield Input(placeholder="Enter name or number", id="good-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip().lower()
        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(self.goods):
                self.dismiss(self.goods[idx][0])
                return
        for gid, name, _, _ in self.goods:
            if text == gid or text == name.lower():
                self.dismiss(gid)
                return
        for gid, name, _, _ in self.goods:
            if gid.startswith(text) or name.lower().startswith(text):
                self.dismiss(gid)
                return
        self.notify(f"Unknown: {text}", severity="warning")

    def action_cancel(self) -> None:
        self.dismiss(None)


def execute_buy_flow(app, session: "GameSession") -> None:
    """Buy overlay goods at the current station."""
    state = session.sf_campaign
    if state is None or state.in_transit:
        app.notify("Not docked at a station.", severity="warning")
        return

    from portlight.content.star_freight import SLICE_STATIONS, SLICE_GOODS
    from portlight.engine.sf_campaign import execute_trade

    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        app.notify("Unknown station.", severity="warning")
        return

    available = []
    for good_id in station.produces:
        good = SLICE_GOODS.get(good_id)
        if good:
            available.append((good_id, good.name, good.base_price, 99))

    if not available:
        app.notify("Nothing for sale here.", severity="warning")
        return

    def on_good_selected(good_id: str | None) -> None:
        if good_id is None:
            return
        good = SLICE_GOODS.get(good_id)
        if not good:
            return
        max_afford = max(1, state.credits // max(1, good.base_price))
        max_qty = min(max_afford, state.ship_cargo_capacity - len(state.ship_cargo))
        if max_qty <= 0:
            app.notify("Cannot buy — hold or credits.", severity="warning")
            return

        def on_qty(qty_str: str | None) -> None:
            if qty_str is None:
                return
            result = execute_trade(state, good_id, "buy", int(qty_str))
            if result.get("error"):
                app.notify(result["error"], severity="error")
            else:
                app.notify(
                    f"Bought {result['quantity']} {result['good']} for {result['total']:,} ₡",
                    severity="information",
                    timeout=5,
                )
                session._save()
                app.refresh_views()

        app.push_screen(TradeDialog("buy", good_id, good.name, max_qty, good.base_price), on_qty)

    app.push_screen(GoodSelectDialog("buy", available), on_good_selected)


def execute_sell_flow(app, session: "GameSession") -> None:
    """Sell overlay cargo at the current station."""
    state = session.sf_campaign
    if state is None or state.in_transit:
        app.notify("Not docked at a station.", severity="warning")
        return

    from portlight.content.star_freight import SLICE_GOODS
    from portlight.engine.sf_campaign import execute_trade

    held = Counter(state.ship_cargo)
    available = []
    for good_id, qty in held.items():
        good = SLICE_GOODS.get(good_id)
        if good:
            available.append((good_id, good.name, good.base_price, qty))

    if not available:
        app.notify("No cargo to sell.", severity="warning")
        return

    def on_good_selected(good_id: str | None) -> None:
        if good_id is None:
            return
        good = SLICE_GOODS.get(good_id)
        qty_held = held[good_id]
        if not good:
            return

        def on_qty(qty_str: str | None) -> None:
            if qty_str is None:
                return
            result = execute_trade(state, good_id, "sell", int(qty_str))
            if result.get("error"):
                app.notify(result["error"], severity="error")
            else:
                app.notify(
                    f"Sold {result['quantity']} {result['good']} for {result['total']:,} ₡",
                    severity="information",
                    timeout=5,
                )
                session._save()
                app.refresh_views()

        app.push_screen(TradeDialog("sell", good_id, good.name, qty_held, good.base_price), on_qty)

    app.push_screen(GoodSelectDialog("sell", available), on_good_selected)
