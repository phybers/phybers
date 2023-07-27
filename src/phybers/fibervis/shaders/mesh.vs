#version 150 core

// Datos de entrada
in vec3 vertexPos;
in vec3 vertexNor;

// Datos de salida
out vec4 color;

uniform mat4 M;
uniform mat4 V;
uniform mat4 P;

// Intensidad de la luz
struct LightInfo {
    vec4 pos;
    vec3 La;
    vec3 Ld;
    vec3 Ls;
};
uniform LightInfo Light;

// Material del modelo
struct MaterialInfo {
    vec3 Ka;
    vec3 Kd;
    vec3 Ks;
    float shininess;    // Coeficiente de reflexion especular
};
uniform MaterialInfo Material;

uniform vec3 meshColor;// = vec3(0.3,0.3,0.3);
uniform float opacity;


void main() {
    vec4 p = V*M*vec4(vertexPos, 1.0);

    vec3 n = normalize(mat3(V*M)*vertexNor);
    vec3 l = normalize(Light.pos.xyz - p.xyz);
    vec3 v = normalize(-p.xyz);
    vec3 r = reflect(-l, n);

    vec3 ambi = Light.La*Material.Ka;
    vec3 diff = max(dot(n, l), 0.0)*Material.Kd*Light.Ld;
    vec3 spec = pow(max(dot(r, v), 0.0), Material.shininess)*Material.Ks*Light.Ls;


    color = vec4(ambi + diff + spec, 1.0)*vec4(meshColor, opacity);
    gl_Position = P*p;
}