function diff(o1: object, o2: object): string[] {
	return Object.keys(o1).filter((key) => {
		return !{}.hasOwnProperty.bind(o2)(key)
	});
}

function inter(o1: object, o2: object): string[] {
	return Object.keys(o1).filter({}.hasOwnProperty.bind(o2));
}

/**
 * Compare objects and call functions in case of missing keys or existing ones.
 * @param {object} o1 first object
 * @param {object} o2 second object
 * @param {Function} add called for each key of o2 - o1
 * @param {Function} del called for each key of o1 - o2
 * @param {Function} upd called for each key of (o2 - o1) | (o1 & o2)
 */
export function compare(
	o1: object,
	o2: object,
	add = (value: string, index: number, array: string[]) => {},
	del = (value: string, index: number, array: string[]) => {},
	upd = (value: string, index: number, array: string[]) => {}
) {
	var add_keys = diff(o2, o1);
	var del_keys = diff(o1, o2);
	var upd_keys = inter(o1, o2).concat(add_keys);

	add_keys.forEach(add);
	del_keys.forEach(del);
	upd_keys.forEach(upd);
}

/**
 * Convert objects of a dict recursively
 * @param {object} data the data to parse
 * @param {object} pattern regular expression to match
 * @param {object} convertor called on value if a key matches
 */
export function convert(
	data: object,
	pattern: RegExp,
	convertor: Function
): object {
	Object.entries(data).forEach(([key, value]) => {
		if (typeof value === 'object' && value !== null) {
			convert(value, pattern, convertor);
		}
		if (typeof key === 'string' && pattern.test(key)) {
			data[key] = convertor(value);
		}
	});
	return data;
}
