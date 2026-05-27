# Alembic Groom Importer

> Import Hair Strands from Alembic file

| 属性 | 值 |
|---|---|
| 中文名 | Alembic 毛发导入器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicHairTranslatorModule` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter) | |

## 用途

该插件为 Unreal Engine 的 Groom（毛发/发束）系统提供 Alembic (.abc) 文件的导入能力。它通过实现 `IGroomTranslator` 接口，将 Alembic 格式中的发束数据解析并转换为引擎内部的 `FHairDescription` 数据结构。

本质上，这是一个**编辑器专用的文件格式翻译器**——它自身不运行时逻辑，只在编辑器的资产导入流程中被调用。插件默认禁用（`EnabledByDefault: false`），需要手动启用才能使用。它还支持 Groom 动画数据的导入（通过 `FGroomAnimationInfo`），可以处理包含时间序列的 Alembic 毛发动画。

## 使用场景

- 你在 DCC 工具（如 Blender、Maya、Houdini）中制作了角色毛发，需要导出为 Alembic 格式再导入 UE5 → 用此插件
- 你有一个包含毛发动画的 Alembic 文件，需要在 UE5 中播放 → 启用此插件后导入即可
- 你使用 Groom 系统进行发束渲染，需要从外部工具获取毛发几何数据 → 此插件是必经之路

## 蓝图用法

该插件不暴露任何蓝图节点。它是一个纯编辑器导入模块，通过引擎的资产导入流程自动调用，无需蓝图交互。

## C++ 用法

该插件的核心是 `FAlembicHairTranslator` 类，实现了 `IGroomTranslator` 接口。对于普通使用者来说，不需要直接调用 C++ API——导入器会在编辑器导入 `.abc` 文件时自动激活。

如需以编程方式调用翻译器，可参考以下方式：

### 头文件引入

```cpp
#include "GroomTranslator.h"  // IGroomTranslator 接口
```

### 基本用法

```cpp
// 创建翻译器实例（通常由 Groom 导入系统内部完成）
FAlembicHairTranslator Translator;

// 检查是否能翻译指定文件
if (Translator.CanTranslate(TEXT("/path/to/hair.abc")))
{
    // 获取支持的格式描述
    FString Format = Translator.GetSupportedFormat();
    
    // 执行翻译：将 Alembic 文件转为 HairDescription
    FHairDescription HairDescription;
    FGroomConversionSettings ConversionSettings;
    bool bSuccess = Translator.Translate(
        TEXT("/path/to/hair.abc"),
        HairDescription,
        ConversionSettings
    );
}
```

### 进阶用法（含动画导入）

```cpp
// 带动画信息的导入流程
FAlembicHairTranslator Translator;
FHairDescription HairDescription;
FGroomConversionSettings ConversionSettings;
FGroomAnimationInfo AnimInfo;

// 第一步：开启翻译并获取动画信息
Translator.BeginTranslation(TEXT("/path/to/animated_hair.abc"));

// 第二步：翻译首帧，同时获取动画元数据
Translator.Translate(
    TEXT("/path/to/animated_hair.abc"),
    HairDescription,
    ConversionSettings,
    &AnimInfo
);

// 第三步：逐帧读取动画数据
float FrameTime = 0.0f;
while (/* 还有后续帧 */)
{
    FHairDescription FrameDescription;
    Translator.Translate(FrameTime, FrameDescription, ConversionSettings);
    // 处理每帧数据...
    FrameTime += 1.0f / AnimInfo.FPS; // 按帧率推进
}

// 第四步：结束翻译，释放资源
Translator.EndTranslation();
```

## Demo 示例

该插件不提供独立可运行的代码示例。它的使用方式是在编辑器中**直接导入**：

1. 启用插件：编辑 → 插件 → 搜索 "Alembic Groom Importer" → 启用并重启
2. 确保已启用前置插件：**HairStrands**（该插件的硬依赖）
3. 在内容浏览器中右键 → Import → 选择 `.abc` 文件
4. 引擎自动识别毛发数据并创建 Groom 资产

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrands`（插件依赖） | 提供 Groom 核心系统、IGroomTranslator 接口、FHairDescription 定义 |
| `AlembicLibrary`（推断） | 底层 Alembic 文件解析库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF 新接口 |
| 2024-05-03 | `1fde5666` | PR #10617: AlembicHairImporterFixes: RootUV from Blender Hair / no RootUV registration when not pars | 修复 Blender 导出的 RootUV 及未解析时的注册问题 |
| 2024-04-16 | `96a33f78` | Fixed potential uninitialized FVectors in AlembicHairImporter. | 修复导入器中 FVector 可能未初始化的问题 |
| 2023-10-13 | `ba50d6b0` | Alembic: Fix import issues with corrupted Alembic files. | 修复损坏 Alembic 文件的导入问题 |
| 2023-08-08 | `bdb4199e` | Remove unnecessary WindowsHWrapper.h & MinWindows.h include - both files will be automatically included | 移除冗余的 Windows 头文件引用 |

### 维护评价

该插件自 2020 年创建以来持续获得维护，但更新频率较低（每年约 1-2 次实质性改动）。最近一次功能性修复在 2024 年 5 月（Blender RootUV 兼容性），2026 年 4 月有一次全局日志宏迁移。

**优点**：
- 功能稳定，作为 Groom 导入管线的关键一环持续存在
- 修复记录表明有持续关注兼容性问题（Blender 导出、损坏文件处理）

**注意事项**：
- 插件默认禁用，需手动启用
- 必须同时启用 **HairStrands** 插件作为前置依赖
- 仅在编辑器中可用（Editor 模块），打包后不包含
- 代码量很小（仅 4 个源文件），维护负担低，风险也低

**推荐**：如果你需要从 DCC 工具导入 Alembic 毛发数据，此插件是必需的。虽然维护不算高频，但核心功能稳定可靠，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter)
- 前置插件：[HairStrands](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)