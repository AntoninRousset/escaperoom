import { _getRemoteStates, _getRemoteTransitions,
	 _setRemoteStates, _setRemoteTransitions } from 'escaperoom-client'
import engine from './engine'
import { MissingPropertyError } from './exceptions.js'

const store = {
  state: engine.state,
  commit: (type, payload = undefined) => {
    return engine.mutations[type](store.state, payload);
  },
  dispatch: (type, payload = undefined) => {
    return engine.actions[type](store, payload);
  },
  getters: new Proxy(engine.getters, {
    get(target, name) { return target[name](store.state, store.getters); }
  }),
};

const stateDefaults = { room: 1, x: 1, y: 1 };

function getLocalStates() {
  return Object.fromEntries(
    store.getters.states.map((state) => [state.name, state])
  );
}

function getLocalTransitions() {
  return Object.fromEntries(store.getters.transitions.map(
    (transition) => [transition.name, transition]
  ));
}

function getRemoteStates() {
  return Object.fromEntries(
    _getRemoteStates().map((state) => [state.name, state])
  );
}

function getRemoteTransitions() {
  return Object.fromEntries(
    _getRemoteTransitions().map((transition) => [transition.name, transition])
  );
}

beforeEach(() => {
  _setRemoteStates([]);
  _setRemoteTransitions([]);
  store.commit('_clean');
    _setRemoteStates([{ id: '1', name: 'a' }, { id: '2', name: 'b' }]);
    _setRemoteTransitions([]);
});

describe('States basics', () => {

  test('Create state', async () => {
    const id = store.commit('addState', { ...stateDefaults, name: 'a' });
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id, name: 'a' }),
    ]));

    await store.dispatch('push');
    expect(getRemoteStates()['a']).toMatchObject({ name: 'a' });
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id, name: 'a' }),
    ]));
  });

  test('Update state', async () => {
    store.commit('setStates', { '1': { id: '1', name: 'a' } });
    _setRemoteStates([{ id: '1', name: 'a' }]);

    store.commit('changeState', { id: '1', name: 'b' });
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id: '1', name: 'b' }),
    ]));

    await store.dispatch('push');
    expect(getRemoteStates()['b']).toMatchObject({ name: 'b' });
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id: '1', name: 'b' }),
    ]));
  });

  test('Destroy state', async () => {
    store.commit('setStates', { '1': { id: '1', name: 'a' } });
    _setRemoteStates([{ id: '1', name: 'a' }]);

    store.commit('removeState', { id: '1' });
    expect(store.getters.states).toEqual([]);

    await store.dispatch('push');
    expect(getRemoteStates()).toEqual({});
    expect(store.getters.states).toEqual([]);
  });

  test('Destroy added state', async () => {
    const id = store.commit('addState', { ...stateDefaults, name: 'a' });

    store.commit('removeState', { id });
    expect(store.getters.states).toEqual([]);

    await store.dispatch('push');
    expect(store.getters.states).toEqual([]);
  });

  test('Destroy created state', async () => {
    const id = store.commit('addState', { ...stateDefaults, name: 'a' });
    await store.dispatch('push');

    store.commit('removeState', { id });
    expect(store.getters.states).toEqual([]);

    await store.dispatch('push');
    expect(store.getters.states).toEqual([]);
  });
});

describe('Transitions basics', () => {

  beforeEach(() => {
    store.commit('_clean');
    _setRemoteStates([{ id: '1', name: 'a' }, { id: '2', name: 'b' }]);
    _setRemoteTransitions([]);
    store.commit('setStates', {
      '1': { id: '1', name: 'a' }, '2': { id: '2', name: 'b' },
    });
  });

  test('Create transition', async () => {
    const id = store.commit(
      'addTransition', { name: 'a->b', src: { id: '1' }, dest: { id: '2' }}
    );
    expect(store.getters.transitions).toEqual(expect.arrayContaining([
      expect.objectContaining(
        { id, name: 'a->b',
          src: expect.objectContaining({ id: '1' }),
          dest: expect.objectContaining({ id: '2' }),
        }
      )
    ]));

    await store.dispatch('push');
    expect(getRemoteTransitions()['a->b']).toMatchObject({ name: 'a->b' });
    expect(store.getters.transitions).toEqual(expect.arrayContaining([
      expect.objectContaining(
        { id, name: 'a->b',
          src: expect.objectContaining({ id: '1' }),
          dest: expect.objectContaining({ id: '2' }),
        }
      )
    ]));
  });

  test('Update transition', async () => {
    store.commit('setTransitions', {
      '1': { id: '1', name: 'a->b', src: '1', dest: '2' },
    });
    _setRemoteTransitions([{ id: '1', name: 'a->b', src: '1', dest: '2' }]);

    store.commit('changeTransition', {
      id: '1', name: 'b->a', src: '2', dest: '1'
    });
    expect(store.getters.transitions).toEqual(expect.arrayContaining([
      expect.objectContaining({
        id: '1', name: 'b->a',
        src: expect.objectContaining({ id: '2' }),
        dest: expect.objectContaining({ id: '1' }),
      })
    ]));

    await store.dispatch('push');
    expect(getRemoteTransitions()['b->a']).toMatchObject({ name: 'b->a' });
    expect(store.getters.transitions).toEqual(expect.arrayContaining([
      expect.objectContaining({
        id: '1', name: 'b->a',
        src: expect.objectContaining({ id: '2' }),
        dest: expect.objectContaining({ id: '1' }),
      })
    ]));
  });

  test('Destroy transition', async () => {
    store.commit('setTransitions', {
      '1': { id: '1', name: 'a->b', src: '1', dest: '2' }
    });
    _setRemoteTransitions([{ id: '1', name: 'a->b', src: '1', dest: '2' }]);

    store.commit('removeTransition', { id: '1' });
    expect(store.getters.transitions).toEqual([]);

    await store.dispatch('push');
    expect(getRemoteTransitions()).toEqual({});
    expect(store.getters.transitions).toEqual([]);
  })

  test('Destroy added transition', async () => {
    const id = store.commit(
      'addTransition', { name: 'a->b', src: { id: '1' }, dest: { id: '2' }}
    );

    store.commit('removeTransition', { id });
    expect(store.getters.transitions).toEqual([]);

    await store.dispatch('push');
    expect(store.getters.transitions).toEqual([]);
  });

  test('Destroy created transition', async () => {
    const id = store.commit(
      'addTransition', { name: 'a->b', src: { id: '1' }, dest: { id: '2' }}
    );

    store.commit('removeTransition', { id });
    expect(store.getters.transitions).toEqual([]);

    await store.dispatch('push');
    expect(store.getters.transitions).toEqual([]);
  });

});

describe('States exceptions', () => {

  test('Removing a state needs it to have an id', async () => {
    expect(() => {
      store.commit('removeState', { name: '1' });
    }).toThrowError(MissingPropertyError)
  });

  test('New state needs x, y and room properties', async () => {
    expect(() => {
      store.commit('addState', { y: 0, room: 1 });
    }).toThrowError(MissingPropertyError)
    expect(() => {
      store.commit('addState', { x: 0, room: 1 });
    }).toThrowError(MissingPropertyError)
    expect(() => {
      store.commit('addState', { x: 0, y: 0 });
    }).toThrowError(MissingPropertyError)
  });

});

describe('States ids', () => {

  test('Pulling does not change ids', async () => {
    store.commit('setStates', {
      '1': { id: '1', name: 'a' },
      '2': { id: '2', name: 'b' },
      '3': { id: '3', name: 'c' },
    });
    _setRemoteStates([
      { id: '1', name: 'a' },
      { id: '2', name: 'b' },
      { id: '3', name: 'c' },
    ]);

    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id: '1', name: 'a' }),
      expect.objectContaining({ id: '2', name: 'b' }),
      expect.objectContaining({ id: '3', name: 'c' }),
    ]));

    await store.dispatch('push');
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id: '1', name: 'a' }),
      expect.objectContaining({ id: '2', name: 'b' }),
      expect.objectContaining({ id: '3', name: 'c' }),
    ]));

    await store.dispatch('pull');
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id: '1', name: 'a' }),
      expect.objectContaining({ id: '2', name: 'b' }),
      expect.objectContaining({ id: '3', name: 'c' }),
    ]));
  });

  test('State creation does not change ids', async () => {
    const id = store.commit('addState', { ...stateDefaults, name: 'a' });
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id, name: 'a' }),
    ]));

    await store.dispatch('push');
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id, name: 'a' }),
    ]));

    await store.dispatch('pull');
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id, name: 'a' }),
    ]));
  });

   test('Update a created state does not change ids', async () => {
    const id = store.commit('addState', { ...stateDefaults, name: 'a' });
    await store.dispatch('push');
    store.commit('changeState', { id, name: 'b' });

    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id, name: 'b' }),
    ]));

    await store.dispatch('push');
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id, name: 'b' }),
    ]));
  });
});

describe('States relationship', () => {

  function checkLocalStates() {
    const states = getLocalStates();
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ id: states['a'].id, name: 'a', parent: null }),
      expect.objectContaining({
        id: states['a.a'].id, name: 'a.a' ,
        parent: expect.objectContaining({ id: states['a'].id })
      }),
      expect.objectContaining({
        id: states['a.a.a'].id, name: 'a.a.a',
        parent: expect.objectContaining({ id: states['a.a'].id })
      }),
    ]));
  }

  test('Removing state should also remove its children', async () => {
    store.commit('setStates', {
      '1': { id: '1', name: 'a', parent: null },
      '2': { id: '2', name: 'a.a', parent: '1' },
      '3': { id: '3', name: 'a.b', parent: '1' },
      '4': { id: '4', name: 'a.a.a', parent: '2' },
      '5': { id: '5', name: 'a.a.b', parent: '2' },
      '6': { id: '6', name: 'a.a.b.a', parent: '5' },
    });
    store.commit('removeState', { id: '2' });
    expect(store.getters.states).toEqual(expect.arrayContaining([
      expect.objectContaining({ name: 'a' }),
      expect.objectContaining({ name: 'a.b' }),
    ]));
  });

  test('Many generations of states can be created (top-down)', async () => {
    const ids = {};
    ids['a'] = store.commit('addState', { ...stateDefaults, name: 'a' });
    ids['a.a'] = store.commit(
      'addState', { ...stateDefaults, name: 'a.a', parent: ids['a'] }
    );
    ids['a.a.a'] = store.commit(
      'addState', { ...stateDefaults, name: 'a.a.a', parent: ids['a.a'] }
    );

    const expectedLocalStates = expect.arrayContaining([
        expect.objectContaining({ id: ids['a'], name: 'a', parent: null }),
        expect.objectContaining({
          id: ids['a.a'], name: 'a.a' ,
          parent: expect.objectContaining({ id: ids['a'] })
        }),
        expect.objectContaining({
          id: ids['a.a.a'], name: 'a.a.a',
          parent: expect.objectContaining({ id: ids['a.a'] })
        }),
    ]);
    expect(store.getters.states).toEqual(expectedLocalStates);

    await store.dispatch('push');
    expect(store.getters.states).toEqual(expectedLocalStates);

    const states = getRemoteStates();
    expect(states['a']).toMatchObject({ name: 'a', parent: null });
    expect(states['a.a']).toMatchObject(
      { name: 'a.a', parent: states['a'].id }
    );
    expect(states['a.a.a']).toMatchObject(
      { name: 'a.a.a', parent: states['a.a'].id }
    );

    await store.dispatch('pull');
    expect(store.getters.states).toEqual(expectedLocalStates);
  });

  test('Many generations of states can be created (down-top)', async () => {
    const ids = {};
    ids['a.a.a'] = store.commit(
      'addState', { ...stateDefaults, name: 'a.a.a' }
    );
    ids['a.a'] = store.commit('addState', { ...stateDefaults, name: 'a.a' });
    ids['a'] = store.commit('addState', { ...stateDefaults, name: 'a' });

    store.commit('changeState', {
      id: ids['a.a.a'], parent: { id: ids['a.a'] }
    });
    store.commit('changeState', {
      id: ids['a.a'], parent: { id: ids['a'] }
    });

    const expectedLocalStates = expect.arrayContaining([
      expect.objectContaining({ id: ids['a'], name: 'a', parent: null }),
      expect.objectContaining({
        id: ids['a.a'], name: 'a.a' ,
        parent: expect.objectContaining({ id: ids['a'] })
      }),
      expect.objectContaining({
        id: ids['a.a.a'], name: 'a.a.a',
        parent: expect.objectContaining({ id: ids['a.a'] })
      }),
    ]);
    expect(store.getters.states).toEqual(expectedLocalStates);

    await store.dispatch('push');
    expect(store.getters.states).toEqual(expectedLocalStates);

    const states = getRemoteStates();
    expect(states['a']).toMatchObject({ name: 'a', parent: null });
    expect(states['a.a']).toMatchObject(
      { name: 'a.a', parent: states['a'].id }
    );
    expect(states['a.a.a']).toMatchObject(
      { name: 'a.a.a', parent: states['a.a'].id }
    );

    await store.dispatch('pull');
    expect(store.getters.states).toEqual(expectedLocalStates);
  });
});

describe('Transitions relationship', () => {

  test('Removing connected state should remove its transition', async () => {
    store.commit('setStates', {
      '1': { id: '1', name: 'a' },
      '2': { id: '2', name: 'b' },
      '3': { id: '3', name: 'c' },
    });
    store.commit('setTransitions', {
      '1': { id: '1', name: 'a->b', src: '1', dest: '2' },
      '2': { id: '2', name: 'b->c', src: '2', dest: '3' },
    });

    store.commit('removeState', { id: '2' });
    expect(store.getters.transitions).toEqual([]);
  });
});
