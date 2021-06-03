let _states = {};

export function _getRemoteStates() {
  return Object.values(_states);
}

export function _setRemoteStates(states) {
  _states = Object.fromEntries(states.map(state => [state.id, state]));
}

export class Configuration {
  constructor(configuration = {}) {
    this.configuration = configuration;
  }
}

export class EngineApi {
  constructor(configuration = {}) {
    this.configuration = configuration;
  }

  _checkConstraints(state) {
    if (state.parent && ! (state.parent in _states)) {
      throw new Error('parent does not exist');
    }
  }

  async statesCreate(requestParameters) {
    for (let id = 1; id <= Object.keys(_states).length + 1; id++) {
      if (!(id.toString() in _states)) {
        const state = { ...requestParameters.state, id };
        try {
          this._checkConstraints(state);
        } catch (fail) {
          throw new Error('Cannot create state', fail);
        }
        _states[id] = state;
        return state;
      }
    }
    throw new Error('Could not find new id for state in creation');
  }

  async statesPartialUpdate(requestParameters) {
    if (requestParameters.id in _states) {
      const state = _states[requestParameters.id];
      Object.assign(state, requestParameters.patchedState);
      return state
    } else {
      throw new Error()  // TODO error_code
    }
  }

  async statesDestroy(requestParameters) {
    if (requestParameters.id in _states) {
      delete _states[requestParameters.id]
    } else {
      throw new Error()  // TODO error_code
    }
  }

  async statesList() {
    return Object.values(_states);
  }
}

