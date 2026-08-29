namespace Orders.Domain;

/// <summary>Porta definida no domínio; implementada em Infrastructure (ADR-0003).</summary>
public interface IOrderRepository
{
    Task<Order?> GetAsync(Guid id, CancellationToken cancellationToken);

    Task SaveAsync(Order order, CancellationToken cancellationToken);
}
