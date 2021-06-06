export class MissingPropertyError extends Error {
    constructor(field, msg) {
        super(msg);
        this.name = 'MissingPropertyError';
    }
}
