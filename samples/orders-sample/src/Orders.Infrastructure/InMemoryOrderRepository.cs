using System.Collections.Concurrent;
using Orders.Domain;

namespace Orders.Infrastructure;

/// <summary>Adapter de persistência. Em produção seria EF Core/Dapper — o domínio não sabe nem precisa saber.</summary>
public sealed class InMemoryOrderRepository : IOrderRepository
{
    private readonly ConcurrentDictionary<Guid, Order> _store = new();

    public Task<Order?> GetAsync(Guid id, CancellationToken cancellationToken)
    {
        _store.TryGetValue(id, out var order);
        return Task.FromResult(order);
    }

    public Task SaveAsync(Order order, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(order);
        _store[order.Id] = order;
        return Task.CompletedTask;
    }
}
