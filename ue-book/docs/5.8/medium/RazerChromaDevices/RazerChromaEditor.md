# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇灯光外设 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Chroma 动画资产、导入工厂、编辑器预览） |
| 模块 | `RazerChromaDevices` (ClientOnlyNoCommandlet), `RazerChromaEditor` (Editor), `RazerChromaSDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices) | |

## 用途

RazerChromaDevices 插件用于在 Unreal Engine 中集成 Razer Chroma RGB 外设灯光效果系统。它允许你导入在 Razer Chroma 官网制作并下载的 `.chroma` 动画文件，在游戏中以 `URazerChromaAnimationAsset` 资产形式管理和播放这些灯光动画，实现游戏事件驱动的外设灯光反馈效果。

该插件解决的核心问题是：将 Razer 外设（键盘、鼠标、耳机等）的 RGB 灯光控制能力引入 UE5，使开发者能够通过 `.chroma` 动画文件在运行时动态操控外设灯光，为玩家打造沉浸式的灯光交互体验。

插件由三个模块组成：
- **RazerChromaSDK**：外部 SDK 封装层，与 Razer Chroma SDK 库进行底层交互
- **RazerChromaDevices**：运行时模块，负责在游戏中播放和控制 Chroma 动画
- **RazerChromaEditor**：编辑器模块，提供 `.chroma` 文件导入、资产管理和编辑器内预览功能

> ⚠️ 此插件处于实验阶段（IsBetaVersion=true，EnabledByDefault=false），API 可能随开发进展发生变化。

## 使用场景

- 你在开发一款支持 Razer 外设的游戏，需要在关键游戏事件（如受到伤害、获得成就、倒计时）时触发外设灯光闪烁效果
- 你在 Razer Chroma 官网设计了 `.chroma` 灯光动画，需要将其导入 UE 项目并在游戏中播放
- 你希望在编辑器中直接预览 Chroma 动画效果，而无需进入 PIE（Play In Editor）
- 你正在开发一款强调感官体验的游戏，想通过外设灯光增强玩家的沉浸感

## 蓝图用法

当前公开的头文件主要集中在编辑器侧（资产操作与导入工厂）。运行时的 BlueprintCallable API 信息较少，需在启用插件后查看 `RazerChromaDevices` 模块的公开头文件。

### 编辑器侧功能

编辑器模块提供以下资产交互功能（非蓝图节点，而是编辑器资产操作）：

| 功能 | 说明 | 所在类 |
|---|---|---|
| 播放动画预览 | 在编辑器中预览 `.chroma` 动画效果 | `FAssetTypeActions_RazerChromaPreviewAction` |
| 停止动画预览 | 停止编辑器中的 Chroma 动画预览 | `FAssetTypeActions_RazerChromaPreviewAction` |
| 导入 `.chroma` 文件 | 自动识别并导入 Razer Chroma 动画文件 | `URazerChromaFactory` |

### 使用示例（蓝图描述）

1. **导入动画**：将从 Razer Chroma 网站下载的 `.chroma` 文件直接拖拽到 Content Browser，插件会通过 `URazerChromaFactory` 自动识别并导入为 `URazerChromaAnimationAsset` 资产。

2. **编辑器预览**：在 Content Browser 中双击 `.chroma` 动画资产，或右键选择 Play 操作，即可在编辑器中预览灯光动画效果，无需进入 PIE 模式。

3. **运行时播放**（需启用插件后查看 `RazerChromaDevices` 模块）：在游戏逻辑中引用 `URazerChromaAnimationAsset` 并通过运行时 API 播放灯光效果。

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块（资产操作相关）
#include "RazerChromaAnimationAssetActions.h"
#include "RazerChromaFactory.h"

// 运行时模块（需启用插件后查看）
#include "RazerChromaAnimationAsset.h"
```

### 基本用法

基于提供的头文件信息，以下是编辑器模块的用法：

```cpp
// RazerChromaFactory 负责 .chroma 文件的导入
// URazerChromaFactory 继承自 UFactory，自动处理以下流程：
// 1. FactoryCanImport() 检测文件扩展名是否为 .chroma
// 2. FactoryCreateBinary() 将二进制数据解析为 URazerChromaAnimationAsset

// RazerChromaAnimationAssetActions 提供编辑器内资产操作
// FAssetTypeActions_RazerChromaPreviewAction 继承自 FAssetTypeActions_Base
// 在 Content Browser 中右键资产时显示 Play/Stop 预览操作
```

### 进阶用法

若需要自定义资产类型的编辑器行为（例如扩展预览功能或添加自定义上下文菜单项），可以参考 `FAssetTypeActions_RazerChromaPreviewAction` 的实现模式：

```cpp
// 自定义资产操作的典型模式
// 1. 继承 FAssetTypeActions_Base
// 2. 实现 GetSupportedClass() 返回关联的资产类
// 3. 通过 GetActions() 添加自定义右键菜单项
// 4. 通过 AssetsActivatedOverride() 处理双击行为
// 5. 使用 CanExecuteXxx() 控制命令可用性
```

## Demo 示例

> 由于 RazerChromaDevices 运行时模块的完整公开 API 未在提供的头文件中展示，以下示例展示编辑器模块的资产操作扩展模式。

```cpp
// MyChromaExtension.h
#pragma once

#include "AssetTypeActions_Base.h"

class URazerChromaAnimationAsset;

/**
 * 自定义 Chroma 动画资产操作示例
 * 展示如何扩展 Razer Chroma 动画资产的编辑器交互
 */
class FMyChromaAssetActions : public FAssetTypeActions_Base
{
public:
    FMyChromaAssetActions(uint32 InCategory) : CategoryBit(InCategory) {}

    // FAssetTypeActions_Base 接口
    virtual FText GetName() const override { return FText::FromString(TEXT("My Chroma Animation")); }
    virtual FColor GetTypeColor() const override { return FColor(0, 255, 0); }
    virtual uint32 GetCategories() override { return CategoryBit; }
    virtual UClass* GetSupportedClass() const override;

private:
    uint32 CategoryBit;
};
```

```cpp
// MyChromaExtension.cpp
#include "MyChromaExtension.h"
#include "RazerChromaAnimationAsset.h"

UClass* FMyChromaAssetActions::GetSupportedClass() const
{
    return URazerChromaAnimationAsset::StaticClass();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RazerChromaSDK` | Razer Chroma SDK 的外部库封装，提供底层灯光控制接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换在 MSVC 和 Clang 间的编译警告兼容性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2025-09-30 | `96cf6b99` | Removed 32-bit support. | 移除 32 位平台支持 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成代码宏以优化编译 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成代码宏以优化编译 |

### 维护评价

**维护不活跃**。该插件自 2024 年 3 月创建以来，从未有过功能性更新——所有近期 commit 均为编译器兼容性修复和引擎级代码迁移，不涉及插件本身的功能开发或 API 演进。

关键风险点：
- **实验性状态**：IsBetaVersion=true 且 EnabledByDefault=false，Epic 明确标注该插件不稳定
- **无实质性功能迭代**：插件的核心功能（动画导入、运行时播放）自初始提交后未见改进
- **API 不稳定**：首次提交信息明确警告 "Expect bugs and changes to the API in the future"
- **外部 SDK 依赖**：依赖 Razer Chroma SDK，受第三方更新节奏影响

**不推荐在生产项目中使用**。该插件适合作为参考或原型验证，正式项目应评估 Razer 官方提供的 Unreal 集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices)