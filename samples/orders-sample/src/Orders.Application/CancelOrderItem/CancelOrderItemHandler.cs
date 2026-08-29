using Orders.Domain;
using Orders.Domain.Events;

namespace Orders.Application.CancelOrderItem;

/// <summary>Orquestra: carrega, chama o domínio, persiste. Não contém regra — o teste de arquitetura garante.</summary>
public sealed class CancelOrderItemHandler(IOrderRepository orders)
{
    public async Task<CancelOrderItemResult> HandleAsync(CancelOrderItemCommand command, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(command);

        var order = await orders.GetAsync(command.OrderId, cancellationToken)
            ?? throw new KeyNotFoundException($"Pedido {command.OrderId} não encontrado.");

        order.CancelItem(command.ItemId); // a regra RN-ORD-012 vive no domínio

        await orders.SaveAsync(order, cancellationToken);

        var events = order.Events.OfType<OrderItemCancelled>().ToList();
        return new CancelOrderItemResult(order.Total, events);
    }
}
