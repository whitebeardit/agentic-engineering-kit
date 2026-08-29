namespace Orders.Domain.Specifications;

public interface ISpecification<in T>
{
    bool IsSatisfiedBy(T candidate);
}
