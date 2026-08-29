namespace Orders.Domain;

/// <summary>Violação de regra de negócio. Carrega o ID da regra (docs/regras) para rastreabilidade.</summary>
public sealed class DomainRuleViolationException : Exception
{
    public string RuleId { get; } = string.Empty;

    public DomainRuleViolationException()
    {
    }

    public DomainRuleViolationException(string message) : base(message)
    {
    }

    public DomainRuleViolationException(string message, Exception innerException) : base(message, innerException)
    {
    }

    public DomainRuleViolationException(string ruleId, string message) : base($"{ruleId}: {message}")
    {
        RuleId = ruleId;
    }
}
