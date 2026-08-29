using Orders.Domain;
using Orders.Domain.Events;

namespace Orders.Application.CancelOrderItem;

public sealed record CancelOrderItemResult(Money NewTotal, IReadOnlyList<OrderItemCancelled> Events);
