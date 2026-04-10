from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from apps.catalog.models import Product


CART_SESSION_KEY = "cart_v2"


@dataclass
class CartLine:
    product: Product
    qty: int

    @property
    def line_total(self) -> int:
        return int(self.product.price) * int(self.qty)


class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.data: Dict[str, int] = self.session.get(CART_SESSION_KEY, {})

    def save(self):
        self.session[CART_SESSION_KEY] = self.data
        self.session.modified = True

    def clear(self):
        self.data = {}
        self.save()

    def add(self, slug: str, qty: int = 1, replace: bool = False):
        qty = max(int(qty), 1)
        if replace or slug not in self.data:
            self.data[slug] = qty
        else:
            self.data[slug] += qty
        self.save()

    def remove(self, slug: str):
        if slug in self.data:
            del self.data[slug]
            self.save()

    def set_qty(self, slug: str, qty: int):
        qty = int(qty)
        if qty <= 0:
            self.remove(slug)
        else:
            self.data[slug] = qty
            self.save()

    def lines(self) -> list[CartLine]:
        slugs = list(self.data.keys())
        products = {p.slug: p for p in Product.objects.filter(slug__in=slugs, is_active=True)}
        out: list[CartLine] = []
        for slug, qty in self.data.items():
            p = products.get(slug)
            if p:
                out.append(CartLine(product=p, qty=int(qty)))
        return out

    @property
    def subtotal(self) -> int:
        return sum(l.line_total for l in self.lines())

    def count(self) -> int:
        return sum(int(q) for q in self.data.values())

    def __len__(self) -> int:
        return self.count()
