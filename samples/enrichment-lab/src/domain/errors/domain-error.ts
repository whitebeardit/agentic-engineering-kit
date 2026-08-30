/** Erro de domínio com status HTTP: o handler central do servidor traduz sem `if` por
 * tipo. */
export class DomainError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly detalhes: string[] = [],
  ) {
    super(message);
    this.name = new.target.name;
  }
}
export class BadRequestError extends DomainError {
  constructor(message: string, detalhes: string[] = []) {
    super(message, 400, detalhes);
  }
}
export class NotFoundError extends DomainError {
  constructor(message: string) {
    super(message, 404);
  }
}
export class ConflictError extends DomainError {
  constructor(message: string) {
    super(message, 409);
  }
}
