#version 150 core

#define cylinderNFace 7
// cylinderMaxVertex = cylinderNFace*2+2
#define cylinderMaxVertex 16

layout(lines) in;
layout(triangle_strip, max_vertices = cylinderMaxVertex) out;

flat in int gs_color[];

out vec4 color;

uniform vec2[cylinderNFace+1] cylinderVertex;

uniform sampler2D colorTable;
uniform int texture1DMax;

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

mat4 rotationMat4Q(vec4 quaternion);
vec4 quaternionFromAngleAndAxis(float angle, vec3 axis);

void main() {
	vec4 baseColor = texelFetch(colorTable, ivec2(gs_color[0]%texture1DMax, gs_color[0]/texture1DMax), 0);

	vec4 point0 = gl_in[0].gl_Position;
	vec4 point1 = gl_in[1].gl_Position;

	vec4 line = point1 - point0;
	vec3 cylinderAxis = vec3(1.0, 0.0, 0.0);

	float angle = acos(dot(cylinderAxis, line.xyz)/(length(cylinderAxis)*length(line.xyz)));
	vec3 axis = cross(cylinderAxis, line.xyz);

	mat4 lineDirection = rotationMat4Q(quaternionFromAngleAndAxis(angle, axis));
	vec4 radiusDelta;

	for (int i=0; i<cylinderNFace+1; i++) {
		radiusDelta = lineDirection*vec4(0.0, cylinderVertex[i], 0.0);

		// Illumination.
		vec4 p = V*M*(point0+radiusDelta);
		vec3 n = normalize(mat3(V*M)*radiusDelta.xyz);
		vec3 l = normalize(vec3(Light.pos - p));
		vec3 v = normalize(-p.xyz);
		vec3 r = reflect(-l, n);

		vec3 ambi = Light.La*Material.Ka;
		vec3 diff = Light.Ld*Material.Kd*max( dot(l, n), 0.0);
		vec3 spec = Light.Ls*Material.Ks*pow(max(dot(r,v), 0.0), Material.shininess);

		// Salidas.
		color = vec4(ambi + diff + spec, 1.0) * baseColor;
		gl_Position = P*V*M*(radiusDelta+point0);
		EmitVertex();


		p = V*M*(point1+radiusDelta);
		l = normalize(vec3(Light.pos - p));
		v = normalize(-p.xyz);
		r = reflect(-l, n);

		diff = Light.Ld*Material.Kd*max( dot(l, n), 0.0);
		spec = Light.Ls*Material.Ks*pow(max(dot(r,v), 0.0), Material.shininess);

		color = vec4(ambi + diff + spec, 1.0) * baseColor;
		gl_Position = P*V*M*(radiusDelta+point1);
		EmitVertex();
	}
}