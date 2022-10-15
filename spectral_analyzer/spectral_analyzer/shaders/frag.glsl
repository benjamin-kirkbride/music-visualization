#version 330

uniform sampler2D sprite_texture;

in vec2 uv;

out vec4 fragColor;

void main() {
    fragColor = texture(sprite_texture, uv);
}