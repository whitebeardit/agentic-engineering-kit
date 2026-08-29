using Orders.Domain;
using Orders.Domain.Events;

namespace Orders.Application.CancelOrderItem;

/// <summary>CANC-07: orquestra — carrega, delega ao domínio, persiste, devolve. Não contém regra (ADR-0003/0004; ArchitectureTests).</summary>
public sealed class CancelOrderItemHandler(IOrderRepository orders)
{
    public async Task<CancelOrderItemResult> HandleAsync(CancelOrderItemCommand command, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(command);

        var order = await orders.GetAsync(command.OrderId, cancellationToken)
            ?? throw new KeyNotFoundException($"Pedido {command.OrderId} não encontrado.");

        order.CancelItem(command.ItemId); // RN-ORD-012 vive no domínio

        await orders.SaveAsync(order, cancellationToken);

        var events = order.Events.OfType<OrderItemCancelled>().ToList();
        return new CancelOrderItemResult(order.Total, events);
    }
}
