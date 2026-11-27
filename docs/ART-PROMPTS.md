# 其他贴图的生图提示词（TraeWork / 通用图片模型）

目标：把墙、箱、旗、水、火、石、门、钥、传送门、狗、猫、花、树、鱼、岩浆这 15 个物件，
统一成和主角（`tools/source/baba-front.png`，金甲骑士 64×64 像素图）一致的风格。

## 使用方法

1. 在 TraeWork / 图片生成里选 **1:1 正方形**，尺寸尽量大（1024 或 768），格式 **PNG**。
2. 如果工具支持「参考图 / 风格参考」，把 `tools/source/baba-front.png` 一起上传，权重不用太高。
3. 复制下面每个「完整提示词」直接生成；建议先做 **墙、箱、门、旗** 四张试风格，满意后再批量。
4. 保存到 `tools/source/ai/<对象id>.png`，例如 `tools/source/ai/wall.png`、`tools/source/ai/dog.png`。
5. 生成完告诉我，我来统一处理：去白底 → 裁切 → 降采样到 64×64 → 量化配色 → 补 1px 描边 → 接入游戏和动画。

动画说明：狗/猫/鱼/花/树/旗/火/传送门先用同一张图做 2 帧（轻微呼吸/发光）；
水 4 帧、岩浆 3 帧会用「无缝平铺 + 横向滚动」做流动，所以这两张请务必生成**无缝贴图**。

## 通用负向提示词（如果工具支持）

```
text, letters, watermark, logo, frame, border, background scenery, multiple objects, realistic photo, 3D render, blurry, soft gradient, drop shadow, ground shadow, cropped object, extra limbs, deformed
```

## 通用风格前缀（每个提示词里已经包含，不需要单独加）

> Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single centered object, front view, thick near-black outline, muted limited palette with warm gold/brown highlights, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.

---

## 完整提示词（逐条复制）

### wall（墙）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single square stone brick wall block filling the frame, front view, grey stone bricks with dark mortar lines and a warm top-left highlight, thick near-black outline, muted limited palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### box（木箱）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single wooden crate with a lighter lid and dark metal corner brackets, centered, front view, thick near-black outline, muted brown and amber palette with warm highlights, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### flag（旗）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single green pennant flag on a short grey pole, flag pointing to the right, centered, front view, thick near-black outline, muted green and cream palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### water（水，无缝贴图）

```
Pixel art seamless tileable water texture for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, stylized blue-teal water surface with small wave crests and pale foam highlights, fills the entire square edge-to-edge, edges must match when tiled, no outer border, no outline around the tile, muted limited palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, no white background, consistent with a golden-armored knight hero sprite.
```

### fire（火）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single small campfire flame with orange outer flame and yellow core, centered, front view, thick near-black outline, muted warm palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### rock（石头）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single rounded grey boulder with a soft top-left highlight and a couple of cracks, centered, front view, thick near-black outline, muted grey palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### door（门）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single wooden door with a rounded top, a small round golden handle and two vertical planks, centered, front view, thick near-black outline, muted brown and amber palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### key（钥匙）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single small golden key standing upright, round bow at the top and two teeth at the bottom, centered, front view, thick near-black outline, muted gold palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### portal（传送门）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single glowing purple portal ring with a lighter center and two small sparkles, centered, front view, thick near-black outline, muted purple and cream palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### dog（狗）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single cute shiba inu dog standing, side view facing right, orange-tan fur with cream belly, ears and curled tail, centered, thick near-black outline, muted warm palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### cat（猫）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single cute grey cat sitting, front view, big eyes, small pink nose, whiskers and striped tail, centered, thick near-black outline, muted grey and cream palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### flower（花）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single red flower with a yellow center, a green stem and two leaves, centered, front view, thick near-black outline, muted red and green palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### tree（树）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single small round tree with a layered green canopy and a short brown trunk, centered, front view, thick near-black outline, muted green and brown palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### fish（鱼）

```
Pixel art game sprite for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, single cute blue fish swimming, side view facing right, pale belly and a small dorsal fin, centered, thick near-black outline, muted blue palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, isolated on a pure white background, consistent with a golden-armored knight hero sprite.
```

### lava（岩浆，无缝贴图）

```
Pixel art seamless tileable lava texture for a top-down puzzle game, 64×64 pixel-art look with chunky pixels and crisp edges, molten orange-red surface with bright yellow cracks, dark crust patches and small glowing bubbles, fills the entire square edge-to-edge, edges must match when tiled, no outer border, no outline around the tile, muted limited palette, flat cel shading, no anti-aliasing, no gradients, no text, no watermark, no shadow, no white background, consistent with a golden-armored knight hero sprite.
```

---

## 生成顺序建议

1. 先做 `wall`、`box`、`door`、`flag` 四张，看风格是否和主角接近；
2. 再补齐 `rock`、`key`、`portal`、`fire`、`water`、`lava`；
3. 最后做 `dog`、`cat`、`fish`、`flower`、`tree` 五只/棵。

## 保存与验收

- 路径：`tools/source/ai/<id>.png`（`id` 用上面的英文名）；
- 白底物件：主体完整、居中、边缘不要太糊、不要投影；
- 水/岩浆：整张图必须铺满、无边框，左右/上下能接上；
- 单张图里只能有一个物件，不要出现文字、边框、地面。
