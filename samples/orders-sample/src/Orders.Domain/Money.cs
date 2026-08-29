namespace Orders.Domain;

/// <summary>RN-ORD-001 — Valor monetário nasce válido ou não nasce. Value object: sem identidade, imutável.</summary>
public readonly record struct Money
{
    public decimal Amount { get; }
    public string Currency { get; }

    public Money(decimal amount, string currency)
    {
        if (amount < 0)
        {
            throw new DomainRuleViolationException("RN-ORD-001", "Valor monetário não pode ser negativo.");
        }

        if (string.IsNullOrWhiteSpace(currency) || currency.Length != 3)
        {
            throw new DomainRuleViolationException("RN-ORD-001", "Moeda deve ser um código ISO de 3 letras.");
        }

        Amount = amount;
        Currency = currency.ToUpperInvariant();
    }

    public static Money Brl(decimal amount) => new(amount, "BRL");

    public Money Add(Money other)
    {
        EnsureSameCurrency(other);
        return new Money(Amount + other.Amount, Currency);
    }

    public Money Multiply(int factor) => new(Amount * factor, Currency);

    public static Money operator +(Money left, Money right) => left.Add(right);

    public static Money operator *(Money money, int factor) => money.Multiply(factor);

    private void EnsureSameCurrency(Money other)
    {
        if (!string.Equals(Currency, other.Currency, StringComparison.Ordinal))
        {
            throw new DomainRuleViolationException("RN-ORD-001", "Não se soma moedas diferentes.");
        }
    }

    public override string ToString() => $"{Amount:0.00} {Currency}";
}
