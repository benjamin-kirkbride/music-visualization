#version 330

// Input from buffers
in vec2 in_position;
in vec2 in_size;

// Outputs to geometry shader
out vec2 position;
out vec2 size;

void main() {
    position = in_position;
    size = in_size;
}