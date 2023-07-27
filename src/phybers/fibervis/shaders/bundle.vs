#version 150 core

in vec3 vertexPos;			// Posicion de las fibras
in vec3 vertexNor;			// Normales 
in float vertexCol;			// Colores

out vec4 color;

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

void main()
{
	// Iluminacion.
	vec4 p = V*M*vec4(vertexPos, 1.0);

	vec3 n = normalize(mat3(V*M)*vertexNor);
	vec3 l = normalize(vec3(Light.pos - p));
	vec3 v = normalize(-p.xyz);
	vec3 r = reflect(-l, n);

	vec3 ambi = Light.La*Material.Ka;
	vec3 diff = Light.Ld*Material.Kd*max( dot(l, n), 0.0);
	vec3 spec = Light.Ls*Material.Ks*pow(max(dot(r,v), 0.0), Material.shininess);
	
	// Salidas.
	int v2c = int(vertexCol);
	color = vec4(ambi + diff + spec, 1.0) * texelFetch(colorTable, ivec2(v2c%texture1DMax, v2c/texture1DMax), 0);
	gl_Position = P*V*M*vec4(vertexPos, 1.0);
}