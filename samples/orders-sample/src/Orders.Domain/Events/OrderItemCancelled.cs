namespace Orders.Domain.Events;

/// <summary>
/// Emitido por RN-ORD-012 (Order.CancelItem). Contrato público, versão 1 — consumido por outros serviços.
/// Mudar ou remover campo = nova versão do evento, nunca alteração in-place (AD-001, rules/contracts.md).
/// </summary>
public sealed record OrderItemCancelled(Guid OrderId, Guid ItemId, Money NewTotal) : IDomainEvent
{
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
}
