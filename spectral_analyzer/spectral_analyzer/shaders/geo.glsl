#version 330

// Configure inputs and outputs for the geometry shader
// We are taking single points form the vertex shader per invocation
// and emitting 4 new vertices creating a quad/sprites
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;            

// A uniform buffer that will automagically contain arcade's projection matrix
uniform Projection {
    uniform mat4 matrix;
} proj;

// Receive the outputs from the vertex shader.
// Since geometry shader can take multiple values from a vertex
// shader we need to define the inputs as arrays.
// We're only getting one vertex at the time in this example,
// but we make an unsized array leaving the rest up to the shader compiler.
in vec2 position[];
in vec2 size[];

// Texture coordinate to fragment shader
out vec2 uv;

void main() {
    // Create some more convenient variables for the input
    vec2 center = position[0];
    vec2 hsize = size[0] / 2.0;

    // Emit a triangle strip of 4 vertices making a triangle.
    // The fragment shader will then fill these triangles in the next stage.

    // Upper left
    gl_Position = proj.matrix * vec4(vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
    uv = vec2(0, 1);
    EmitVertex();

    // lower left
    gl_Position = proj.matrix * vec4(vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
    uv = vec2(0, 0);
    EmitVertex();

    // upper right
    gl_Position = proj.matrix * vec4(vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
    uv = vec2(1, 1);
    EmitVertex();

    // lower right
    gl_Position = proj.matrix * vec4(vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
    uv = vec2(1, 0);
    EmitVertex();

    EndPrimitive();
}