<template>
	<div
		:class="{state: true, single: ! hasChildren}"
		ref="root"
		:style="{
			left: position.x + 'px',
			top: position.y + 'px',
			height: size.height + 'px',
			width: size.width + 'px'
		}">
		{{info.name}}
		<div
			class="fsm"
			v-if="fsm"
			:style="{
				height: size.height + 'px',
				width: size.width + 'px'
			}">
			<e-state v-for="state in info.children" :info="state"/>
		</div>
	</div>
</template>

<script>
import {mapState} from 'vuex'

export default {
	name: 'EState',
	props: ['info'],

	data() {
		return {
			root: null,
			gridStep: 50,
		}
	},

	mounted() {

		this.root = this.$refs['root'];

    if (this.info.id == 4) {
      setInterval(() => {
        this.info.x = 3;
        this.info.y = 2;
      }, 2000)
    }

	},

	computed: {

		...mapState(['fsm', 'darkMode']),

		hasChildren() {
			return Object.keys(this.info.children).length > 0;
		},

		position() {
			return {
				x: this.info.x * this.gridStep,
				y: this.info.y * this.gridStep
			};
		},

		size() {

			if (this.root === null)
				return {height: '', width: ''};

			return {
				height: this.root.scrollHeight,
				width: this.root.scrollWidth
			};
		},
	},

	watch: {

		darkMode(newValue, oldValue) {
		},

    "info.children": {
      handler: function(newValue) {
        console.log('Info changed');
        console.log('>>>', this.root.style);
        this.root.style.width = this.root.scrollWidth;
        this.root.style.height = this.root.scrollHeight;
      },
      deep: true,
    }

	},

	methods: {

    computeSize() {

    }

	},
}
</script>
<style lang="scss">
	@import "../scss/colors.scss";

	div {
		position: absolute;

		&.fsm {
			left: 0;
			top: 0;
		}

		&.state {
			border: solid;

			position: absolute;
			overflow: visible;

		}

		&.single {
			border-radius: 15px;
		}
	}
</style>
