<template>
  <div
    class="machine"
    :style="{
      width: w * gridStep + 'px',
      height: h * gridStep + 'px',
		}"
    @click.self="deselectState('all')"
    >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="`0 0 ${w * this.gridStep} ${h * this.gridStep}`"
      :width="w * this.gridStep + 'px'"
      :height="h * this.gridStep + 'px'"
      @click.self="deselectState('all')">
      <defs>
        <marker id="triangle" viewBox="0 0 10 10"
          refX="8" refY="4"
          markerUnits="userSpaceOnUse"
          markerWidth="10" markerHeight="10"
          orient="auto">
          <path
            d="M 10 4 L 0 0 L 0 8 z"
            stroke-width="0"
            fill="#aaa"/>
        </marker>
      </defs>
      <e-transition
        v-for="(trans, i) in transitions"
        :i="i"
        :points="getTransitionsPoints(i)"
        />
    </svg>
    <e-state
      v-for="(state, i) in states"
      :i="i"
      :name="state.name"
      :x="stateGeom[i].x * gridStep"
      :y="stateGeom[i].y * gridStep"
      :w="stateGeom[i].w * gridStep"
      :h="stateGeom[i].h * gridStep"
      :selected="selectedStates.includes(i)"
      :dragged="typeof draggedStates[i] !== 'undefined'"
      @click="deselectState('all'); selectState(i)"
      @shiftclick="selectState(i)"
      @drag="(dx, dy) => dragState(i, dx, dy)"
    />
  </div>
</template>

<script>
import {mapState} from 'vuex'
import {defineAsyncComponent,defineComponent} from 'vue';
import ETransition from './transition'
import Mouse from '../utils/mouse.vue'

export default {

  components: {

    // dynamic import of EState to avoid circular dependencies
    'e-state': defineAsyncComponent(() =>
      import('./state.vue')
    ),
    'e-transition': ETransition,

  },

	name: 'EMachine',
  mixins: [Mouse],
	props: {
    'states': {
      type: Array,
      default: [],
    },
    'transitions': {
      type: Array,
      default: [],
    },
    'gridStep': {
      type: Number,
      default: 20,
    },
    'padding': {
      type: Number,
      default: 1,
    },
    'headerHeight': {
      type: Number,
      default: 2,
    },
  },
  emits: [],

	data() {
		return {
      selectedStates: [],
      draggedStates: {},
		}
	},

	computed: {

		...mapState(['fsm', 'darkMode']),

    w() {
      return Math.max(0, ...[...this.states.keys()].map((j) => {
        return this.states[j].x + this.computeStateW(j);
      })) + 2 * this.padding;
    },

    h() {
      return Math.max(0, ...[...this.states.keys()].map((j) => {
        return this.states[j].y + this.computeStateH(j);
      })) + 2 * this.padding;
    },

    stateGeom() {
      return [...this.states.keys()].map((i) => {
        return {
          i: i,
          x: this.computeStateX(i),
          y: this.computeStateY(i),
          w: this.computeStateW(i),
          h: this.computeStateH(i),
        };
      });
    },

    anchorGeom() {
      return this.stateGeom.map((geom) => {
        let x = geom.x;
        let y = geom.y;
        let w = geom.w;
        let h = geom.h;
        return {
          i: geom.i,
          O:  {orient: 'O',  x: x + w / 2, y: y + h / 2},
          N:  {orient: 'N',  x: x + w / 2, y: y        },
          NE: {orient: 'NE', x: x + w    , y: y        },
          E:  {orient: 'E',  x: x + w    , y: y + h / 2},
          SE: {orient: 'SE', x: x + w    , y: y + h    },
          S:  {orient: 'S',  x: x + w / 2, y: y + h    },
          SW: {orient: 'SW', x: x        , y: y + h    },
          W:  {orient: 'W',  x: x        , y: y + h / 2},
          NW: {orient: 'NW', x: x        , y: y        },
        };
      });
    },

    transitionGeom() {
      return this.transitions.map((trans) => {
        return this.getBestAnchor(trans.src, trans.dest);
      });
    },
	},

	methods: {

    computeStateX(i) {
      let state = this.states[i];
      let x = state.x + this.padding;

      while (state.parent !== null) {

      if (state.parent === i)
        throw `State ${i} has itself as parent`;

        state = this.states[state.parent];
        x += state.x + this.padding;
      }

      return x;
    },

    computeStateY(i) {
      let state = this.states[i];
      let y = state.y + this.padding;

      while (state.parent !== null) {

      if (state.parent === i)
        throw `State ${i} has itself as parent`;

        state = this.states[state.parent];
        y += state.y + this.padding + this.headerHeight;
      }

      return y;
    },

    computeStateW(i) {

      let children = this.getStateChildren(i);

      // no children
      if (children.length === 0)
        return 2;

      if (children.includes(i))
        throw 'State ${i} has itself as parent';

      return Math.max(...children.map((j) => {
        return this.states[j].x + this.computeStateW(j);
      })) + 2 * this.padding;
    },

    computeStateH(i) {

      let children = this.getStateChildren(i);

      // no children
      if (children.length === 0)
        return 2;

      if (children.includes(i))
        throw 'State ${i} has itself as parent';

      return Math.max(...children.map((j) => {
        return this.states[j].y + this.computeStateH(j);
      })) + 2 * this.padding + this.headerHeight;
    },

    getStateChildren(i, depth=1) {

      if (depth === 'inf')
        depth = -1;

      let children = Array();

      children = children.concat([...this.states.keys()].filter((j) => {
        return this.states[j].parent === i;
      }));

      if (depth != 1) {

        let grandchildren = Array();

        for (let j of children)
          grandchildren = grandchildren.concat(this.getStateChildren(j, depth - 1));

        children = children.concat(grandchildren);
      }

      return children;
    },

    getStateParents(i, depth=1) {

      if (depth === 'inf')
        depth = -1;

      if (typeof this.states[i] === 'undefined')
        return [];

      if (this.states[i].parent === null)
        return [];

      let parents = [this.states[i].parent];

      if (depth != 1) {

        let grandparents = Array();

        for (let j of parents)
          grandparents = grandparents.concat(this.getStateParents(j, depth - 1));

        parents = parents.concat(grandparents);
      }

      return parents;
    },



    selectState(i) {

      if (i === 'all')
        i = [...this.states.keys()];

      this.selectedStates = this.selectedStates.concat(i);
    },

    deselectState(i) {

      if (i === 'all') {
        this.selectedStates = [];
        return;
      }

      if (typeof i === 'number')
        i = [i];

      this.selectedStates = this.selectedStates.filter((j) => {
        return i.includes(j);
      });

    },

    getBestAnchor(i, j, m) {

      let state1 = this.stateGeom[i];
      let state2 = this.stateGeom[j];

      let anchors1 = [];
      let anchors2 = [];

      if (this.anchorGeom[j].O.x > this.anchorGeom[i].O.x) {
        anchors1.push(this.anchorGeom[i].E);
        anchors2.push(this.anchorGeom[j].W);
      } else {
        anchors1.push(this.anchorGeom[i].W);
        anchors2.push(this.anchorGeom[j].E);
      }

      if (this.anchorGeom[j].O.y > this.anchorGeom[i].O.y) {
        anchors1.push(this.anchorGeom[i].S);
        anchors2.push(this.anchorGeom[j].N);
      } else {
        anchors1.push(this.anchorGeom[i].N);
        anchors2.push(this.anchorGeom[j].S);
      }

      function distanceFromAnchor(anchor, x, y) {
        if (anchor.orient == 'N')
          return anchor.y - y;
        if (anchor.orient == 'E')
          return x - anchor.x;
        if (anchor.orient == 'S')
          return y - anchor.y;
        if (anchor.orient == 'W')
          return anchor.x - x;
        throw `Invalid orientation: ${anchor.orient}`
      }

      let src = null;
      let dest = null;
      let dmax = null;

      for (let a1 of anchors1) {
        for (let a2 of anchors2) {

          let d = Math.min(...[
            distanceFromAnchor(a1, a2.x, a2.y), 
            distanceFromAnchor(a2, a1.x, a1.y), 
          ]);

          if (dmax === null || d > dmax) {
            dmax = d;
            src = a1;
            dest = a2;
          }
        }
      }

      // if dest state pointing back to src state
      let cabs = 0;
      let c = 0;
      let cd = 0;
      if (this.getStateOutgoingTransitions(j).map((k) => {
        return this.transitions[k].dest;
      }).includes(i)) {
        cabs = 0.25
      }

      let d = distanceFromAnchor(src, dest.x, dest.y);
      if (src.orient == 'N' || src.orient == 'S') {

        if (dest.orient == 'S' || dest.orient == 'N') {

          c = (dest.y > src.y) ? -cabs : cabs;
          cd = (dest.x > src.x) ? cabs : -cabs;

          if (src.x === dest.x) {
            return [
              {x: src.x + c,  y: src.y},
              {x: dest.x + c, y: dest.y},
            ];
          }

          return [
            {x: src.x + c,  y: src.y},
            {x: src.x + c,  y: (src.y + dest.y) / 2 + cd},
            {x: dest.x + c, y: (src.y + dest.y) / 2 + cd},
            {x: dest.x + c, y: dest.y},
          ];

        }

        return [
          {x: src.x + c,  y: src.y},
          {x: src.x + c,  y: dest.y + c},
          {x: dest.x,     y: dest.y + c},
        ];

      } else {

        if (dest.orient == 'W' || dest.orient == 'E') {

          c = (dest.x > src.x) ? -cabs : cabs;
          cd = (dest.y > src.y) ? cabs : -cabs;

          if (src.y === dest.y) {
            return [
              {x: src.x,  y: src.y + c},
              {x: dest.x, y: dest.y + c},
            ];
          }

          return [
            {x: src.x,                     y: src.y + c},
            {x: (src.x + dest.x) / 2 + cd, y: src.y + c},
            {x: (src.x + dest.x) / 2 + cd, y: dest.y + c},
            {x: dest.x,                    y: dest.y + c},
          ];
        }

        return [
          {x: src.x,      y: src.y + c},
          {x: dest.x + c, y: src.y + c},
          {x: dest.x + c, y: dest.y},
        ];
      }
    },

    getTransitionsPoints(i) {
      return this.transitionGeom[i].map(p => {
        return {x: p.x * this.gridStep, y: p.y * this.gridStep,};
      });
    },

    getStateIngoingTransitions(i) {
      return [...this.transitions.keys()].filter((j) => {
        return this.transitions[j].dest === i;
      })
    },

    getStateOutgoingTransitions(i) {
      return [...this.transitions.keys()].filter((j) => {
        return this.transitions[j].src === i;
      });
    },

    getStateTransitions(i) {
      return [...this.getStateIngoingTransitions(i),
              ...this.getStateOutgoingTransitions(i)];
    },

    stateMousedown(e, i) {
      console.log('down', i);
    },

    stateMouseup(e, i) {
      console.log('up', i);
    },

    dragState(i, dx, dy) {

      let draggedStates = [i];

      // add selected states if multiple
      if (this.selectedStates.length > 1)
        draggedStates = draggedStates.concat(this.selectedStates);

      // remove states that already have a dragged parent
      let invalidStates = Array();
      for (let j of draggedStates) {
        for (let k of this.getStateParents(j)) {
          if (draggedStates.includes(k) && ! invalidStates.includes(j))
            invalidStates.push(j);
        }
      }

      draggedStates = draggedStates.filter(j => !invalidStates.includes(j));

      // save dragged states
      for (let j of draggedStates) {
        if (typeof this.draggedStates[j] === 'undefined') {
          this.draggedStates[j] = {
            x0: this.states[j].x,
            y0: this.states[j].y,
          }
        }
      }

      for (let j in this.draggedStates) {
        this.states[j].x = Math.max(0, this.draggedStates[j].x0 + Math.round(dx / this.gridStep));
        this.states[j].y = Math.max(0, this.draggedStates[j].y0 + Math.round(dy / this.gridStep));
      }
    },

	},

  watch: {
    'mouse.down'(newv, oldv) {
      if (!newv)
        this.draggedStates = {};
    }, 
  }
}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

	div.machine {
    min-width: 100%;
    min-height: 100%;
    display: inline-block;
    position: relative;
    background: url("../../resources/grid32.png");
	}

</style>
