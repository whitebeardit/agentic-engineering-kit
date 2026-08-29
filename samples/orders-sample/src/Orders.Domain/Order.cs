using Orders.Domain.Events;

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
}
