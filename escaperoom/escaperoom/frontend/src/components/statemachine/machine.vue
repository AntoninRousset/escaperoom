<template>
  <div
    class="machine"
    :style="{
      width: w * this.gridStep + 'px',
      height: h * this.gridStep + 'px',
		}">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="`0 0 ${w * this.gridStep} ${h * this.gridStep}`"
      :width="w * this.gridStep + 'px'"
      :height="h * this.gridStep + 'px'"
    >
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
      @select="selectState"
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
		}
	},

	computed: {

		...mapState(['fsm', 'darkMode']),

    w() {
      return Math.max(0, ...Array(...this.states.keys()).map((j) => {
        return this.states[j].x + this.computeStateW(j);
      })) + 2 * this.padding;
    },

    h() {
      return Math.max(0, ...Array(...this.states.keys()).map((j) => {
        return this.states[j].y + this.computeStateH(j);
      })) + 2 * this.padding;
    },

    stateGeom() {
      return Array(...this.states.keys()).map((i) => {
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

    getStateChildren(i) {
      return Array(...this.states.keys()).filter((j) => {
        return this.states[j].parent === i;
      });
    },

    selectState(i) {

      if (i === 'all')
        i = Array(...this.states.keys());

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
      let maxd = null;

      for (let a1 of anchors1) {
        for (let a2 of anchors2) {

          let d = Math.min(...[
            distanceFromAnchor(a1, a2.x, a2.y), 
            distanceFromAnchor(a2, a1.x, a1.y), 
          ]);

          if (maxd === null || d > maxd) {
            maxd = d;
            src = a1;
            dest = a2;
          }
        }
      }

      let d = distanceFromAnchor(src, dest.x, dest.y);
      if (src.orient == 'N' || src.orient == 'S') {

        if (dest.orient == 'S' || dest.orient == 'N') {

          if (src.x === dest.x) {
            return [
              {x: src.x,  y: src.y},
              {x: dest.x, y: dest.y},
            ];
          }

          return [
            {x: src.x,  y: src.y},
            {x: src.x,  y: (src.y + dest.y) / 2},
            {x: dest.x, y: (src.y + dest.y) / 2},
            {x: dest.x, y: dest.y},
          ];

        }

        return [
          {x: src.x,  y: src.y},
          {x: src.x,  y: dest.y},
          {x: dest.x, y: dest.y},
        ];

      } else {

        if (dest.orient == 'W' || dest.orient == 'E') {

          if (src.y === dest.y) {
            return [
              {x: src.x,  y: src.y},
              {x: dest.x, y: dest.y},
            ];
          }

          return [
            {x: src.x,                y: src.y},
            {x: (src.x + dest.x) / 2, y: src.y},
            {x: (src.x + dest.x) / 2, y: dest.y},
            {x: dest.x,               y: dest.y},
          ];
        }

        return [
          {x: src.x,   y: src.y},
          {x: dest.x,  y: src.y},
          {x: dest.x,  y: dest.y},
        ];
      }

      //    NW     |       N       |    NE
      //           |               |
      //  ---------+---------------+---------
      //           |               |
      //    W      |       O       |     E
      //           |               |
      //  ---------+---------------+---------
      //           |               |
      //    SW     |       S       |    SE

    },

    getTransitionsPoints(i) {
      return this.transitionGeom[i].map(p => {
        return {x: p.x * this.gridStep, y: p.y * this.gridStep,};
      });
    },
	},
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
