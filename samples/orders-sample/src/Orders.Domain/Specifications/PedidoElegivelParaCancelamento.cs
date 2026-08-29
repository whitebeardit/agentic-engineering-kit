namespace Orders.Domain.Specifications;

/// <summary>RN-ORD-012 (predicado): só pedido aberto admite cancelamento de item. Reutilizável em consulta e comando.</summary>
public sealed class PedidoElegivelParaCancelamento : ISpecification<Order>
{
    public bool IsSatisfiedBy(Order candidate)
    {
        ArgumentNullException.ThrowIfNull(candidate);
        return candidate.Status == OrderStatus.Aberto;
    }
}
