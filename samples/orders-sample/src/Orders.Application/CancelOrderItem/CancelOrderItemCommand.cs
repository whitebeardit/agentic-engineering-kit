namespace Orders.Application.CancelOrderItem;

public sealed record CancelOrderItemCommand(Guid OrderId, Guid ItemId);
