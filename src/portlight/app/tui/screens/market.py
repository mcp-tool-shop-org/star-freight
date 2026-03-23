"""Market screen — maritime-themed interactive buy/sell.

Features:
- Numbered good selection with price preview
- Profit/loss indicator in selection list
- Quantity input with max affordability
- Trade result notifications with silver amounts
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession


class TradeDialog(ModalScreen[str | None]):
    """Modal dialog for quantity input with maritime styling."""

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
                f"[bold #e9c46a]\u2693 {self.action.title()} {self.good_name}[/bold #e9c46a]\n\n"
                f"  Price: [yellow]{self.price}[/yellow] silver each\n"
                f"  Max:   [cyan]{self.max_qty}[/cyan] units"
                + (f" ([yellow]{total_max:,}[/yellow] silver)" if self.action == "buy" else "")
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
    """Modal dialog to select a good — shows prices and margins."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, action: str, goods: list[tuple[str, str, int, int]]) -> None:
        super().__init__()
        self.action = action
        # (good_id, display_name, price, extra_info)
        self.goods = goods

    def compose(self) -> ComposeResult:
        with Vertical(id="input-area"):
            lines = [f"[bold #e9c46a]\u2693 {self.action.title()} which good?[/bold #e9c46a]", ""]
            for i, (gid, name, price, extra) in enumerate(self.goods, 1):
                price_str = f"[yellow]{price}[/yellow]" if price > 0 else "[dim]-[/dim]"
                extra_str = ""
                if extra > 0 and self.action == "buy":
                    extra_str = f" [dim](stock: {extra})[/dim]"
                elif extra > 0 and self.action == "sell":
                    extra_str = f" [dim](held: {extra})[/dim]"
                lines.append(f"  [cyan]{i:2d}[/cyan]. {name:16s} {price_str} silver{extra_str}")
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
    """Launch the buy flow with price previews."""
    port = session.current_port
    if not port:
        app.notify("\u2693 Not docked at a port.", severity="warning")
        return

    from portlight.content.goods import GOODS
    available = []
    for slot in sorted(port.market, key=lambda s: s.buy_price):
        good = GOODS.get(slot.good_id)
        if good and slot.buy_price > 0 and slot.stock_current > 0:
            max_afford = session.world.captain.silver // slot.buy_price
            if max_afford > 0:
                available.append((slot.good_id, good.name, slot.buy_price, slot.stock_current))

    if not available:
        app.notify("Nothing affordable to buy.", severity="warning")
        return

    def on_good_selected(good_id: str | None) -> None:
        if good_id is None:
            return
        slot = next((s for s in port.market if s.good_id == good_id), None)
        if not slot:
            return
        good = GOODS.get(good_id)
        max_afford = session.world.captain.silver // slot.buy_price if slot.buy_price > 0 else 0
        max_qty = min(max_afford, slot.stock_current)

        def on_qty(qty_str: str | None) -> None:
            if qty_str is None:
                return
            qty = int(qty_str)
            result = session.buy(good_id, qty)
            if isinstance(result, str):
                app.notify(f"\u2717 {result}", severity="error")
            else:
                app.notify(
                    f"\u2713 Bought {result.quantity} {good.name} for {result.total_cost:,} silver",
                    severity="information",
                    timeout=5,
                )
                app.refresh_views()

        app.push_screen(TradeDialog("buy", good_id, good.name, max_qty, slot.buy_price), on_qty)

    app.push_screen(GoodSelectDialog("buy", available), on_good_selected)


def execute_sell_flow(app, session: "GameSession") -> None:
    """Launch the sell flow with held quantities."""
    port = session.current_port
    if not port:
        app.notify("\u2693 Not docked at a port.", severity="warning")
        return

    cap = session.world.captain
    from portlight.content.goods import GOODS
    available = []
    for cargo in cap.cargo:
        good = GOODS.get(cargo.good_id)
        if good and cargo.quantity > 0:
            slot = next((s for s in port.market if s.good_id == cargo.good_id), None)
            sell_price = slot.sell_price if slot else 0
            available.append((cargo.good_id, good.name, sell_price, cargo.quantity))

    if not available:
        app.notify("No cargo to sell.", severity="warning")
        return

    def on_good_selected(good_id: str | None) -> None:
        if good_id is None:
            return
        cargo_item = next((c for c in cap.cargo if c.good_id == good_id), None)
        if not cargo_item:
            return
        good = GOODS.get(good_id)
        slot = next((s for s in port.market if s.good_id == good_id), None)
        sell_price = slot.sell_price if slot else 0

        def on_qty(qty_str: str | None) -> None:
            if qty_str is None:
                return
            qty = int(qty_str)
            result = session.sell(good_id, qty)
            if isinstance(result, str):
                app.notify(f"\u2717 {result}", severity="error")
            else:
                profit = result.total_revenue - result.total_cost
                profit_str = ""
                if profit > 0:
                    profit_str = f" [green](+{profit:,} profit)[/green]"
                elif profit < 0:
                    profit_str = f" [red]({profit:,} loss)[/red]"
                app.notify(
                    f"\u2713 Sold {result.quantity} {good.name} for {result.total_revenue:,} silver{profit_str}",
                    severity="information",
                    timeout=5,
                )
                app.refresh_views()

        app.push_screen(TradeDialog("sell", good_id, good.name, cargo_item.quantity, sell_price), on_qty)

    app.push_screen(GoodSelectDialog("sell", available), on_good_selected)
