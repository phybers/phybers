#version 150 core

layout(lines) in;
layout(line_strip, max_vertices = 2) out;

in vec3 vsNormal[];
in float vsVertex2Fib[];

out vec4 color;

uniform mat4 M;
uniform mat4 V;
uniform mat4 P;

struct LightInfo {
	vec4 pos;				// Posicion de la luz.
	vec3 La;				// Intensidad de luz ambiental.
	vec3 Ld;				// Intensidad de luz difusa.
	vec3 Ls;				// Intensidad de luz especular.
};
uniform LightInfo Light;

struct MaterialInfo {
	vec3 Ka;				// Reflectividad ambiental.
	vec3 Kd;				// Reflectividad difusa.
	vec3 Ks;				// Reflectividad especular.
	float shininess;		// Coeficiente de reflexion especular.
};
uniform MaterialInfo Material;

uniform sampler2D colorTable;
// uniform usampler1D fiberValidator;
uniform usampler2D fiberValidator;		// bundleAssignment
// uniform usampler2D bundleAssignment;
uniform float alpha;
uniform int texture1DMax;
uniform int bundleTex1DMax;
uniform int notAssigned;

void main() {
	int intV2F = int(vsVertex2Fib[0]);
	ivec2 bundleFetcher = ivec2(intV2F%texture1DMax, intV2F/texture1DMax);

	int bundle = int(texelFetch(fiberValidator, bundleFetcher, 0).r);

	ivec2 bundleColorFetcher = ivec2(bundle%bundleTex1DMax, bundle/bundleTex1DMax);
	vec4 baseColor = texelFetch(colorTable, bundleColorFetcher, 0);

	// ------------------------------------------------------------------------------------------
	// fetch visibles bundles and compare the current bundle with the ones that will be displayed
	// ------------------------------------------------------------------------------------------
	if (alpha > 1.5f) {
		if (bundle < notAssigned)
			for (int i=0; i<gl_in.length(); i++) {
				vec4 p = V*M*gl_in[i].gl_Position;

				vec3 n = normalize(mat3(V*M)*vsNormal[i]);
				vec3 l = normalize(vec3(Light.pos - p));
				vec3 v = normalize(-p.xyz);
				vec3 r = reflect(-l, n);

				vec3 ambi = Light.La*Material.Ka;
				vec3 diff = Light.Ld*Material.Kd*max( dot(l, n), 0.0);
				vec3 spec = Light.Ls*Material.Ks*pow(max(dot(r,v), 0.0), Material.shininess);
					
				// Salidas.
				color = vec4(ambi + diff + spec, 1.0) * baseColor;
				gl_Position = P*p;
				EmitVertex();
			}
	}

	else if (bundle >= notAssigned)
			for (int i=0; i<gl_in.length(); i++) {
				vec4 p = V*M*gl_in[i].gl_Position;

				vec3 n = normalize(mat3(V*M)*vsNormal[i]);
				vec3 l = normalize(vec3(Light.pos - p));
				vec3 v = normalize(-p.xyz);
				vec3 r = reflect(-l, n);

				vec3 ambi = Light.La*Material.Ka;
				vec3 diff = Light.Ld*Material.Kd*max( dot(l, n), 0.0);
				vec3 spec = Light.Ls*Material.Ks*pow(max(dot(r,v), 0.0), Material.shininess);
				
				// Salidas.
				color = vec4(((ambi + diff + spec) * baseColor.rgb), alpha);
				gl_Position = P*p;
				EmitVertex();
			}

	EndPrimitive();
}