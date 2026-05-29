# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices

| 属性 | 值 |
|---|---|
| 中文名 | DMX引擎 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (UncookedOnly), `DMXEditor` (Runtime), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMXEngine 是 Unreal Engine 中用于处理 DMX（数字多路复用器）协议的核心插件。DMX 是灯光和舞台设备控制的标准协议，广泛应用于现场演出、影视制作和虚拟制片。这个插件为 Unreal Engine 提供了完整的 DMX 设备通信、数据解析和蓝图集成能力，使得开发者可以在引擎内直接控制真实的 DMX 灯具和设备，或者模拟 DMX 信号流。

## 使用场景

- **影视虚拟制片**：使用 LED 墙配合 DMX 灯光，实现真实的光效与虚拟场景的同步
- **现场演出**：在 Unreal 中设计灯光程序，通过 DMX 协议控制舞台上的真实灯具
- **主题公园与沉浸式体验**：控制交互式灯光装置和特效设备
- **建筑可视化**：模拟智能照明系统的效果和动画
- **游戏开发**：集成 DMX 设备到游戏体验中，例如用于实景娱乐（LBE）

## 蓝图用法

该插件在蓝图中提供了多个自定义节点，主要用于获取和解析 DMX 设备数据。所有节点都集中在“DMX”分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get DMX Attribute Values` | 从指定的 Fixture Patch 中获取所有属性值，并以 Map 形式输出 | `UK2Node_GetDMXAttributeValues` |
| `Get DMX Fixture Patch` | 获取一个 DMX Fixture Patch 的引用 | `UK2Node_GetDMXFixturePatch` |
| `Get DMX Fixture Type` | 获取一个 DMX Fixture Type 的引用 | `UK2Node_GetDMXFixtureType` |
| `Cast Patch To Type` | **已弃用** - 用于检查 Fixture Patch 是否属于给定的 Fixture Type，并获取其属性值 | `UDEPRECATED_K2Node_CastPatchToType` |

### 使用示例（蓝图描述）

**获取 DMX 属性值示例**：
1. 在蓝图中添加 `Get DMX Attribute Values` 节点
2. 将 `DMX Fixture Patch` 引用连接到节点的输入引脚
3. 节点会根据输入的 Fixture Patch 所关联的 Fixture Type 动态生成对应的属性输出引脚
4. 连接 `Is Success` 引脚来检查操作是否成功
5. 从各个属性引脚（如 `Red`, `Green`, `Blue`, `Intensity` 等）获取 DMX 通道的当前值

**获取 DMX 引用示例**：
1. 添加 `Get DMX Fixture Patch` 或 `Get DMX Fixture Type` 节点
2. 在节点属性中设置对应的 DMX Library 和实体引用
3. 节点输出可用于其他 DMX 操作的引用对象

## C++ 用法

由于 DMXBlueprintGraph 模块主要是为蓝图节点提供支持的编辑器模块，其 C++ 接口相对较少。主要是一些自定义的 Pin 类型和布局类。

### 头文件引入

```cpp
#include "DMXBlueprintGraphModule.h"
```

### 基本用法

从源码中提取的基本用法示例，主要涉及模块初始化和自定义注册：

```cpp
// 获取 DMXBlueprintGraph 模块实例
FDMXBlueprintGraphModule& DMXBlueprintGraphModule = FDMXBlueprintGraphModule::Get();

// 检查模块是否可用
if (FDMXBlueprintGraphModule::IsAvailable())
{
    // 模块已加载，可以使用相关功能
}
```

### 进阶用法

自定义图表面板引脚工厂的使用（在编辑器扩展中）：

```cpp
// 引入自定义引脚工厂头文件
#include "DMXGraphPanelPinFactory.h"

// 创建自定义引脚工厂实例
TSharedPtr<FDMXGraphPanelPinFactory> DMXGraphPanelPinFactory = MakeShareable(new FDMXGraphPanelPinFactory());

// 注册到编辑器（通常在模块的 StartupModule 中自动完成）
FEdGraphUtilities::RegisterVisualPinFactory(DMXGraphPanelPinFactory);
```

## Demo 示例

由于 DMXBlueprintGraph 模块主要提供编辑器扩展功能，没有运行时演示代码。以下是一个展示如何在编辑器中注册自定义详情自定义的示例：

```cpp
// DMXBlueprintGraphCustomization.h
#pragma once

#include "CoreMinimal.h"

class FDMXBlueprintGraphCustomization
{
public:
    static void RegisterCustomizations();
    static void UnregisterCustomizations();
    
private:
    static void RegisterFixtureTypeCustomizations();
    static void UnregisterFixtureTypeCustomizations();
};
```

```cpp
// DMXBlueprintGraphCustomization.cpp
#include "DMXBlueprintGraphCustomization.h"
#include "PropertyEditorModule.h"

void FDMXBlueprintGraphCustomization::RegisterCustomizations()
{
    RegisterFixtureTypeCustomizations();
}

void FDMXBlueprintGraphCustomization::UnregisterCustomizations()
{
    UnregisterFixtureTypeCustomizations();
}

void FDMXBlueprintGraphCustomization::RegisterFixtureTypeCustomizations()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    
    // 注册自定义详情面板（实际类名需要根据插件中的类来确定）
    // PropertyModule.RegisterCustomClassLayout("DMXEntityFixtureType", FOnGetDetailCustomizationInstance::CreateStatic(&FDmxFixtureTypeCustomization::MakeInstance));
    // PropertyModule.NotifyCustomizationModuleChanged();
}

void FDMXBlueprintGraphCustomization::UnregisterFixtureTypeCustomizations()
{
    if (FModuleManager::Get().IsModuleLoaded("PropertyEditor"))
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
        
        // 注销自定义详情面板
        // PropertyModule.UnregisterCustomClassLayout("DMXEntityFixtureType");
        // PropertyModule.NotifyCustomizationModuleChanged();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXRuntime` | DMX 核心运行时功能，提供实体、设备管理等基础类 |
| `DMXEditor` | DMX 编辑器功能，提供 UI 和资产编辑支持 |
| `DMXProtocol` | DMX 协议实现，处理 Art-Net, sACN 等具体协议 |
| `DMXFixture` | DMX Fixture（灯具）定义和管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `96d3b290` | DMX - Fix a crash when trying to edit a sequence with a fixture patch that no longer contains a mode | 修复当编辑包含不再有模式的 Fixture Patch 的序列时发生的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将各种 VP 资产移动到不同的资产类别，并迁移它们 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 格式 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | [IsSavingPackage] 相关更新 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now | 移除被 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5` 保护的包含，删除现在已经不再需要的头文件 |

### 维护评价

DMXEngine 是 Unreal Engine 虚拟制片工作流中的重要组成部分，自 2020 年创建以来持续得到维护。从最近的提交记录可以看出，插件仍在活跃维护中，近期修复了与序列编辑相关的崩溃问题，并进行了代码现代化（如迁移日志宏）。虽然最后一次实质性功能更新没有明确记录，但 2026 年的提交显示 Epic Games 团队仍在关注该插件的稳定性和兼容性。该插件对于需要与 DMX 设备交互的虚拟制片项目是**推荐使用**的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine/Tests) (如果存在)