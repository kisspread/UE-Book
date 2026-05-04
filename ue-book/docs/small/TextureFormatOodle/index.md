# Oodle Texture

> Oodle Texture plugin

| 属性 | 值 |
|---|---|
| 分类 | Compression |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | TextureFormatOodle (UncookedOnly) |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/TextureFormatOodle) | |

## 用途

TextureFormatOodle 将 [Oodle Texture](https://www.radgametools.com/oodle-texture.htm)（RAD Game Tools 的纹理压缩库，现属 Epic Games）集成到 UE5 的纹理压缩管线中。它替代了默认的纹理压缩器，为 BC1–BC7 格式提供更高质量的纹理编码，同时支持 **RDO（率失真优化）** 能力——在可控的视觉质量损失下大幅减小纹理数据体积。

核心能力：
- **BCN 编码**：替代 UE 默认编码器处理 BC1/BC2/BC3/BC4/BC5/BC6H/BC7
- **RDO 压缩**：通过 lambda 参数控制质量/体积权衡，在 DDC 缓存命中后不影响 Cook 速度
- **多版本 SDK 共存**：内置 Oodle 2.9.5–2.9.14 共 10 个版本的 DLL，按纹理资产中记录的版本号自动选择对应版本编码器
- **并行编码**：支持多线程并行压缩，集成 Oodle Jobify 线程池系统

该插件默认启用且类型为 `UncookedOnly`——仅在编辑器和 Cook 流程中加载，运行时不需要。

## 使用场景

- 你的项目需要尽可能减小纹理包体大小（特别是移动端或下载游戏）→ 用 Oodle Texture RDO 调高 lambda
- 你希望获得比 UE 默认编码器更高的 BCN 编码质量 → 启用此插件（默认已启用）
- 你需要对不同纹理组（LODGroup）设定不同的压缩强度 → 通过 `LossyCompressionAmount` 按组调整 lambda
- 你需要调试纹理压缩结果，确认哪些纹理确实经过了 Oodle 编码 → 使用 `bDebugColor` 功能

## INI 配置

插件从 `Engine.ini` 读取配置（节名为 `[TextureFormatOodleSettings]`），默认值在首次使用时自动生成。

### 配置项

```ini
[TextureFormatOodleSettings]
; 用纯色填充编码后的纹理，颜色由 BCN 格式决定
; 可以快速确认哪些纹理经过了 Oodle 编码，哪些未使用 BCN 压缩
bDebugColor=False

; 全局 lambda 缩放因子，影响所有纹理的 RDO lambda（包括默认值和每纹理覆盖值）
; 推荐在项目后期微调包体大小时才修改此值（如 0.9 或 1.1）
GlobalLambdaMultiplier=1.0

; DebugDump 过滤器（可选），只导出匹配的纹理到 Saved/OodleDebugImages/
DebugDumpFilter=

; 日志级别 0=不输出, 1=仅大纹理, 2=全部
LogVerbosity=0
```

### Lambda（RDO 质量控制）

Lambda 是控制 Oodle Texture RDO 的核心参数，控制大小与质量的权衡。Lambda 的来源按优先级：

1. **每纹理覆盖**：在纹理编辑器中设置 `LossyCompressionAmount`（Lowest → Highest）
2. **LODGroup 继承**：如果纹理设为 Default，则从所属 LODGroup 继承
3. **全局默认**：从项目 Texture Compression Settings 中获取

```ini
; 示例：在 DeviceProfile 中按 LODGroup 调整
[GlobalDefaults DeviceProfile]
@TextureLODGroups=Group
TextureLODGroups=(Group=TEXTUREGROUP_World,...,LossyCompressionAmount=TLCA_High)
+TextureLODGroups=(Group=TEXTUREGROUP_WorldNormalMap,...,LossyCompressionAmount=TLCA_Low)
```

`TLCA_None` 会完全禁用 RDO（不推荐，需要极高质量时用 `TLCA_Lowest`）。

### 启用 TextureFormatOodle 格式前缀

默认情况下，插件通过 `TFO_` 前缀接管标准格式。在 `BaseEngine.ini` 中配置：

```ini
[AlternateTextureCompression]
TextureCompressionFormat="TextureFormatOodle"
TextureFormatPrefix="TFO_"
```

启用后，`DXT1` 等格式名变为 `TFO_DXT1`，由 Oodle 编码器处理。

## 蓝图用法

此插件不暴露任何蓝图接口。它是一个纯编辑器/Cook 管线插件，所有功能通过 INI 配置和编辑器 UI（纹理资产属性）控制。

## C++ 用法

此插件不设计为被外部代码直接调用。它实现了 `ITextureFormat` 接口，由 UE 的纹理压缩管线自动调度。以下是内部实现的关键类供参考：

### 核心类

| 类 | 说明 |
|---|---|
| `FTextureFormatOodle` | 实现 `ITextureFormat` 接口，处理 `CompressImage` / `DecodeImage` |
| `FTextureFormatOodleConfig` | 从 INI 读取配置并转为 Oodle 参数 |
| `FOodleTextureVTable` | 管理单个版本 Oodle DLL 的动态加载和函数指针 |
| `FOodleTextureBuildFunction` | DDC Build Function，用于 Derived Data Cache 键生成 |

### 支持的纹理格式

| UE 格式名 | Oodle BCN | 说明 |
|---|---|---|
| `TFO_DXT1` | BC1 | RGB，可选 1-bit Alpha |
| `TFO_DXT3` | BC2 | RGBA，显式 Alpha |
| `TFO_DXT5` | BC3 | RGBA，插值 Alpha |
| `TFO_DXT5n` | BC3 | 法线贴图（旧格式，推荐用 BC5） |
| `TFO_AutoDXT` | BC1/BC3 | 根据是否有 Alpha 自动选择 |
| `TFO_BC4` | BC4U | 单通道 |
| `TFO_BC5` | BC5U | 双通道（法线贴图） |
| `TFO_BC6H` | BC6U | HDR |
| `TFO_BC7` | BC7RGBA | 高质量 RGBA |

### 多版本 SDK

插件内置以下 Oodle Texture SDK 版本的动态库（`Sdks/` 目录下）：

2.9.5、2.9.6、2.9.7、2.9.8、2.9.9、2.9.10、2.9.11、2.9.12、2.9.13、2.9.14

每个纹理资产记录了编码时使用的 SDK 版本，后续重压缩时会加载对应版本的 DLL。未标记版本的旧纹理默认使用 2.9.5。可通过 INI 配置项 `AlternateTextureCompression/OodleTextureSdkVersionIfNone` 覆盖默认回退版本。

### 平台支持

| 平台 | 动态库 |
|---|---|
| Win64 x64 | `oo2tex_win64_{version}.dll` |
| Win64 ARM64 | `oo2tex_9_winuwparm64_{version}.dll`（仅 2.9.14+） |
| Linux x64 | `liboo2texlinux64.{version}.so` |
| Linux ARM64 | `liboo2texlinuxarm64.{version}.so` |
| macOS | `liboo2texmac64.{version}.dylib` |

## 模块依赖

此插件为内部管线插件，不建议外部模块直接依赖。其内部依赖关系为：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、字符串、平台抽象 |
| `DerivedDataCache` | DDC 缓存桶（FCacheBucket） |
| `ImageCore` | FImage 图像数据结构 |
| `TextureBuild` | 纹理构建管线（FTextureBuildFunction） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-07-24 | `dbd913e` | BC6 纹理在 Oodle 2.9.12 上可能崩溃，升级到 2.9.13 |
| 2025-05-30 | `d04f859` | 添加 Windows ARM64 的 placeholder DLL/LIB（仅 2.9.14 可用） |
| 2025-05-15 | `c5275de` | 启用 Oodle 2.9.14 SDK |

### 维护评价

- **状态**: 活跃维护
- 创建于 2021 年 4 月，已有 5 年以上历史
- 2025 年仍有频繁更新（SDK 升级、平台扩展、bug 修复）
- Oodle SDK 版本从 2.9.5 持续升级到 2.9.14，表明 Epic 在积极维护
- 近期新增了 Windows ARM64 支持
- **推荐使用**：这是 UE5 默认启用的标准纹理压缩方案，生产环境应保持启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/TextureFormatOodle)
- [Oodle Texture 官方文档](https://www.radgametools.com/oodle-texture.htm)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/TextureFormatOodle/Source/Private/Jobify)（Jobify 示例代码）
