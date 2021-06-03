export class IdError extends Error {
    constructor(field, msg) {
        super(msg);
        this.name = 'IdError';
    }
}

export class MissingIdError extends IdError {
    constructor(field, msg) {
        super(msg);
        this.name = 'MissingIdError';
    }
}
