namespace Orders.Domain.Specifications;

/// <summary>RN-ORD-012 / CANC-06 (predicado): só pedido Aberto admite cancelamento de item. Reutilizável em comando e consulta (AD-002).</summary>
public sealed class PedidoElegivelParaCancelamento : ISpecification<Order>
{
    public bool IsSatisfiedBy(Order candidate)
    {
        ArgumentNullException.ThrowIfNull(candidate);
        return candidate.Status == OrderStatus.Aberto;
    }
}
