namespace Orders.Domain.Events;

/// <summary>Emitido por RN-ORD-012. Contrato público: mudar campo = versionar (rules/contracts.md).</summary>
public sealed record OrderItemCancelled(Guid OrderId, Guid ItemId, Money NewTotal) : IDomainEvent
{
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
}
