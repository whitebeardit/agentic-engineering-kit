using Orders.Domain.Events;
using Orders.Domain.Specifications;

namespace Orders.Domain;

/// <summary>Agregado Pedido. Toda regra de negócio de pedido entra por aqui — nunca por controller ou handler (ADR-0003).</summary>
public sealed class Order
{
    private readonly List<OrderItem> _items = [];
    private readonly List<IDomainEvent> _events = [];

    public Order(Guid id)
    {
        Id = id;
        Status = OrderStatus.Aberto;
    }

    public Guid Id { get; }
    public OrderStatus Status { get; private set; }
    public IReadOnlyList<OrderItem> Items => _items;
    public IReadOnlyList<IDomainEvent> Events => _events;

    public Money Total
    {
        get
        {
            var total = Money.Brl(0);
            foreach (var item in _items)
            {
                if (!item.Cancelled)
                {
                    total += item.Subtotal;
                }
            }

            return total;
        }
    }

    public OrderItem AddItem(string sku, int quantity, Money unitPrice)
    {
        if (Status != OrderStatus.Aberto)
        {
            throw new DomainRuleViolationException("RN-ORD-003", "Só pedido aberto recebe itens.");
        }

        var item = new OrderItem(Guid.NewGuid(), sku, quantity, unitPrice);
        _items.Add(item);
        return item;
    }

    public void Invoice()
    {
        if (Status != OrderStatus.Aberto)
        {
            throw new DomainRuleViolationException("RN-ORD-004", "Só pedido aberto pode ser faturado.");
        }

        Status = OrderStatus.Faturado;
    }

    /// <summary>RN-ORD-012 — Cancelamento parcial (CANC-01..05). Teste: RN_ORD_012_* · Doc: docs/regras/pedidos.md · Spec: .specs/features/001-cancelamento-parcial</summary>
    public void CancelItem(Guid itemId)
    {
        if (!new PedidoElegivelParaCancelamento().IsSatisfiedBy(this))
        {
            throw new DomainRuleViolationException("RN-ORD-012", "Pedido faturado não admite cancelamento de item.");
        }

        var item = _items.Find(i => i.Id == itemId)
            ?? throw new DomainRuleViolationException("RN-ORD-012", "Item não pertence ao pedido.");

        if (item.Cancelled)
        {
            return; // idempotente: cancelar duas vezes não emite dois eventos
        }

        item.Cancel();
        _events.Add(new OrderItemCancelled(Id, itemId, Total));
    }
}
