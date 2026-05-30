# Spatialization

> Plugin featuring a variety of basic audio spatialization solutions.

| 属性 | 值 |
|---|---|
| 中文名 | 音频空间化 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `Spatialization` (Runtime), `SpatializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-25 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization) | |

## 用途

Spatialization 插件提供了一组**基础的音频空间化方案**。它旨在作为更高级、复杂空间化系统（如基于物理的HRTF）的轻量级替代或补充，或用于快速原型开发。其核心解决的是将3D音频位置信息映射到2D扬声器布局（如立体声、环绕声）的问题，提供诸如立体声扩展、简单头部相关传输函数（HRTF）滤波等效果。

## 使用场景

-   你的项目只需要基础的空间音效，不需要复杂的双耳录音或物理建模。
-   你需要为游戏内的物体（如脚步声、武器声）快速添加简单的空间定位效果。
-   你正在开发一个对性能要求较高的游戏，需要一个轻量级的空间化方案。
-   你需要在编辑器中预览和调整空间化设置。

## 蓝图用法

蓝图中主要通过空间化器（Spatializer）接口来配置和控制音频源的空间化行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Spatialization Settings` | 为音频组件设置空间化参数（如算法、强度） | `UAudioMixerBlueprintLibrary` |
| `Get Spatialization Settings` | 获取音频组件当前的空间化设置 | `UAudioMixerBlueprintLibrary` |
| `Set Spatialization Enabled` | 启用或禁用音频组件的空间化效果 | `UAudioComponent` |
| `Get Spatialization Enabled` | 查询音频组件的空间化是否启用 | `UAudioComponent` |

### 使用示例（蓝图描述）

1.  在一个 `Audio Component` 的细节面板中，找到 `Spatialization` 部分。
2.  勾选 `Enable Spatialization` 以启用。
3.  点击 `Spatialization Plugin Settings` 旁的下拉菜单，选择 `Spatialization` 插件提供的某个算法（如 `Panning`）。
4.  在蓝图图表中，你可以使用 `Set Spatialization Settings` 节点，在运行时动态更改这些设置，例如根据玩家装备切换空间化模式。

## C++ 用法

### 头文件引入

```cpp
#include "IAudioExtensionPlugin.h"
```

### 基本用法

获取并设置音频组件的空间化器。
*来源：测试用例 `SpatializationTest.cpp`*

```cpp
// 获取音频组件上的空间化器对象
TScriptInterface<IAudioSpatialization> Spatializer = MyAudioComponent->GetSpatializationPlugin();
if (Spatializer)
{
    // 检查空间化是否启用
    bool bIsEnabled = Spatializer->IsSpatializationEnabled();

    // 设置新的空间化算法（这里以Panning为例，实际需匹配插件提供的名称）
    FSpatializationSettings NewSettings;
    NewSettings.SpatializationMethod = ESpatializationMethod::Panning;
    Spatializer->SetSpatializationSettings(NewSettings);
}
```

### 进阶用法

在音频渲染线程中直接使用空间化器处理音频缓冲区。
*来源：测试用例 `AudioMixerSpatializationTest.cpp`*

```cpp
// 假设在音频线程上下文中，已有一个有效的FSpatializationPluginDelegate
void MySpatializationCallback(const FSoundSourceSpatializationParams& Params, FAlignedFloatBuffer& OutBuffer)
{
    if (SpatializationPluginHandle.IsValid())
    {
        // 获取指向空间化处理函数的指针
        FSpatializationPluginDelegate::FProcessSpatializationAudioCallback* ProcessCallback = SpatializationPluginHandle->GetSpatializationAudioCallback();
        if (ProcessCallback)
        {
            // 执行实际的空间化音频处理
            (*ProcessCallback)(Params, OutBuffer);
        }
    }
}
```

## Demo 示例

一个最小的自定义空间化器示例，演示如何基于此插件框架进行扩展。
*注意：实际项目中通常直接使用插件提供的现有空间化器。*

```cpp
// MyCustomSpatializer.h
#pragma once
#include "IAudioExtensionPlugin.h"

class FMyCustomSpatializer : public IAudioSpatialization
{
public:
    // 实现IAudioSpatialization接口
    virtual bool IsSpatializationEnabled() const override { return bEnabled; }
    virtual void SetSpatializationEnabled(bool bInEnabled) override { bEnabled = bInEnabled; }
    virtual void SetSpatializationSettings(const FSpatializationSettings& InSettings) override { Settings = InSettings; }
    virtual FSpatializationSettings GetSpatializationSettings() const override { return Settings; }

private:
    bool bEnabled = true;
    FSpatializationSettings Settings;
};
```

```cpp
// MyCustomSpatializer.cpp
#include "MyCustomSpatializer.h"
// 插件模块通常会在启动时注册自定义的空间化器工厂。
```

## 模块依赖

从模块的 `Build.cs` 文件中提取。使用此插件，你的模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 核心音频混合系统，空间化插件的基础依赖。 |
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器音频菜单变更，与插件核心功能无关。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 代码生成优化，添加内联宏以减少编译依赖，属底层改进。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files... | 构建系统调整，统一符号导出规范，无功能变化。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录结构批量更新，属于项目维护。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件内的外部链接更新为HTTPS，属安全合规性修改。 |

### 维护评价

Spatialization 是一个**基础且稳定**的插件，创建于2019年。从近期提交历史看，其**核心音频空间化功能自2021年以来没有实质性更新**（最后的实质性代码变更在更早的提交中）。近年来的提交主要集中在构建系统、代码规范和项目结构的维护上，属于Epic对引擎整体代码库的例行优化。

-   **优点**：稳定、轻量、作为基础功能与引擎版本长期兼容。
-   **注意**：它提供的方案比较基础，如果你的项目需要先进的双耳音频或基于物理的HRTF，应考虑使用 `Oculus Audio` 或 `Steam Audio` 等第三方插件，或查看 `AudioMixer` 模块中的更高级空间化选项。
-   **推荐**：适用于原型开发、性能敏感场景，或作为理解UE音频空间化架构的起点。对于生产级项目的复杂音频需求，可能需要评估其功能是否足够。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization/Tests)