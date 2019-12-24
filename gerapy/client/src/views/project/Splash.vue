<template>
	<div>
		<el-form-item :label="$lang.columns.url">
			<el-input
				v-model="config.uri" class="inline"
				:placeholder="$lang.columns.url"
				size="small"></el-input>
		</el-form-item>

		<el-form-item :label="$lang.columns.moduleSettings">
			<span slot="label">
				{{$lang.columns.moduleSettings}}
				<i class="el-icon-info" :title="$lang.tips.splashSettings"/>
			</span>
			<el-input
				v-model="config.custom_settings" class="inline"
				:placeholder="$lang.columns.attrValue"
				size="small"></el-input>

		</el-form-item>

	</div>
</template>

<script>
	export default {
		name: 'Splash',
		props: {
			config: {
				type: Object,
				default: {
					custom_settings: null,
					uri: null
				}
			},
			items: {
				type: Array
			},
			onAddInput: {
				type: Function
			},
			onDeleteInput: {
				type: Function
			}
		},
		methods: {
		}
	}
</script>
