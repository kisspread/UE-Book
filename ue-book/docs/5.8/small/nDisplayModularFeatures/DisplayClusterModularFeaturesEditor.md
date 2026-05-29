# nDisplay Modular Features

> Modular Features for nDisplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 模块化功能接口 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterLightCardExtender` (Runtime), `DisplayClusterModularFeaturesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplayModularFeatures) | |

## 用途

这是一个为 Unreal Engine 的 **nDisplay** 大型显示墙/集群渲染系统提供扩展能力的插件。它的核心作用是定义了一套“模块化功能”接口，允许第三方模块（或插件）为 nDisplay 的特定功能（例如媒体初始化）提供自定义的实现。

该插件本身不包含任何具体内容资产（如蓝图、材质），其价值在于提供了一个标准化的扩展点。它主要解决在复杂的 nDisplay 集群渲染环境中，如何灵活地支持不同厂商的媒体源、输出设备或特定的媒体传输协议。开发者可以通过实现此插件定义的接口，无缝地将自己的媒体处理逻辑集成到 nDisplay 的管线中，而无需修改 nDisplay 核心代码。

## 使用场景

- 你正在使用 **nDisplay** 构建一个由多台 PC 驱动的 LED 虚拟摄影棚或大型投影系统，需要集成一个非 Unreal 默认支持的、来自专业硬件厂商（如 Barco, Disguise 等）的媒体流。
- 你需要在 nDisplay 集群中自定义媒体流的初始化过程，例如在不同集群节点间设置特定的单播或多播传播模式。
- 你是媒体硬件或中间件的开发者，希望将你的产品以标准化、即插即用的方式提供给 nDisplay 用户。

## 蓝图用法

此插件定义的接口 `IDisplayClusterModularFeatureMediaInitializer` 是一个纯 C++ 的 `IModularFeature`，它主要面向模块开发者，而非直接面向蓝图设计师。因此，该插件**没有提供**可供蓝图直接调用的核心节点。

其使用方式是通过 C++ 实现该接口，并在模块的 `StartupModule` 中将其注册为一个命名的模块化功能。之后，nDisplay 的媒体管理系统会动态发现并调用这些已注册的功能。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterModularFeatureMediaInitializer.h"
```

### 基本用法

要扩展 nDisplay 的媒体初始化能力，你需要创建一个新模块，并实现 `IDisplayClusterModularFeatureMediaInitializer` 接口。

**1. 声明你的实现类 (MyMediaInitializer.h)：**

```cpp
// MyMediaInitializer.h
#pragma once
#include "IDisplayClusterModularFeatureMediaInitializer.h"

class FMyMediaInitializer : public IDisplayClusterModularFeatureMediaInitializer
{
public:
    // IModularFeature 接口
    virtual ~FMyMediaInitializer() = default;

    // 检查媒体对象是否支持
    virtual bool IsMediaObjectSupported(const UObject* MediaObject) override;

    // 检查媒体源和输出是否兼容
    virtual bool AreMediaObjectsCompatible(const UObject* MediaSource, const UObject* MediaOutput) override;

    // 获取支持的传播类型
    virtual bool GetSupportedMediaPropagationTypes(const UObject* MediaSource, const UObject* MediaOutput, EMediaStreamPropagationType& OutPropagationTypes) override;

    // 为分块（Tile）模式初始化媒体对象
    virtual void InitializeMediaObjectForTile(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo, const FIntPoint& TilePos) override;

    // 为全帧模式初始化媒体对象
    virtual void InitializeMediaObjectForFullFrame(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo) override;
};
```

**2. 实现核心函数 (MyMediaInitializer.cpp)：**

```cpp
// MyMediaInitializer.cpp
#include "MyMediaInitializer.h"
#include "MediaSource.h" // 假设你处理的是特定类型的媒体源

bool FMyMediaInitializer::IsMediaObjectSupported(const UObject* MediaObject)
{
    // 示例：仅支持特定类型的媒体源
    const UMyCustomMediaSource* MySource = Cast<UMyCustomMediaSource>(MediaObject);
    return MySource != nullptr;
}

bool FMyMediaInitializer::AreMediaObjectsCompatible(const UObject* MediaSource, const UObject* MediaOutput)
{
    // 示例：检查自定义的兼容性逻辑
    // ...
    return true; // 根据实际逻辑返回
}

bool FMyMediaInitializer::GetSupportedMediaPropagationTypes(const UObject* MediaSource, const UObject* MediaOutput, EMediaStreamPropagationType& OutPropagationTypes)
{
    if (!MediaSource || !MediaOutput)
    {
        return false;
    }

    // 示例：声明支持单播和本地多播
    OutPropagationTypes = EMediaStreamPropagationType::Unicast | EMediaStreamPropagationType::LocalMulticast;
    return true;
}

void FMyMediaInitializer::InitializeMediaObjectForTile(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo, const FIntPoint& TilePos)
{
    // 在此为媒体对象设置分块相关的参数
    // 例如：设置分辨率偏移、分块索引等
    // UMyCustomMediaOutput* Output = Cast<UMyCustomMediaOutput>(MediaObject);
    // if (Output) { Output->SetTilePosition(TilePos); }
}

void FMyMediaInitializer::InitializeMediaObjectForFullFrame(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo)
{
    // 在此为媒体对象设置全帧参数
    // 例如：设置完整的分辨率
    // UMyCustomMediaOutput* Output = Cast<UMyCustomMediaOutput>(MediaObject);
    // if (Output) { Output->SetResolution(FIntPoint(1920, 1080)); }
}
```

**3. 注册模块化功能 (你的模块 StartupModule 中)：**

```cpp
void FMyDisplayExtensionModule::StartupModule()
{
    // 创建实例并注册
    MyMediaInitializer = MakeShareable(new FMyMediaInitializer());
    IModularFeatures::Get().RegisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::ModularFeatureName, MyMediaInitializer.Get());
}

void FMyDisplayExtensionModule::ShutdownModule()
{
    // 注销
    IModularFeatures::Get().UnregisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::ModularFeatureName, MyMediaInitializer.Get());
    MyMediaInitializer.Reset();
}
```

### 进阶用法

更复杂的用法涉及在接口实现中处理来自 `FMediaObjectOwnerInfo` 的详细信息，并根据 `OwnerType`（ICVFX Camera, Viewport, Backbuffer）执行不同的初始化逻辑。例如，你可能需要为 ICVFX 摄影机设置特定的色彩空间映射，而为后缓冲视口设置不同的传输参数。

```cpp
void FMyAdvancedMediaInitializer::InitializeMediaObjectForFullFrame(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo)
{
    if (OwnerInfo.OwnerType == FMediaObjectOwnerInfo::EMediaObjectOwnerType::ICVFXCamera)
    {
        // 针对 ICVFX 摄影机的特殊初始化
        // 例如，从 OwnerInfo.OwnerName 找到对应的相机组件并读取其属性
        // UMyMediaOutput* MediaOutput = Cast<UMyMediaOutput>(MediaObject);
        // MediaOutput->SetCameraSpecificSettings(...);
    }
    else if (OwnerInfo.OwnerType == FMediaObjectOwnerInfo::EMediaObjectOwnerType::Viewport)
    {
        // 针对视口的初始化
    }
    // ...
}
```

## Demo 示例

**MyCustomMediaPlugin.h**
```cpp
// MyCustomMediaPlugin.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyCustomMediaPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FMyMediaInitializer> MediaInitializer;
};
```

**MyCustomMediaPlugin.cpp**
```cpp
// MyCustomMediaPlugin.cpp
#include "MyCustomMediaPlugin.h"
#include "IDisplayClusterModularFeatureMediaInitializer.h"
#include "IModularFeatures.h"

// 简单的媒体初始化器实现
class FMyMediaInitializer : public IDisplayClusterModularFeatureMediaInitializer
{
public:
    virtual bool IsMediaObjectSupported(const UObject* MediaObject) override { return true; /* 仅作示例 */ }
    virtual bool AreMediaObjectsCompatible(const UObject* MediaSource, const UObject* MediaOutput) override { return true; }
    virtual bool GetSupportedMediaPropagationTypes(const UObject* MediaSource, const UObject* MediaOutput, EMediaStreamPropagationType& OutPropagationTypes) override
    {
        OutPropagationTypes = EMediaStreamPropagationType::LocalUnicast;
        return true;
    }
    virtual void InitializeMediaObjectForTile(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo, const FIntPoint& TilePos) override {}
    virtual void InitializeMediaObjectForFullFrame(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo) override {}
};

void FMyCustomMediaPluginModule::StartupModule()
{
    MediaInitializer = MakeShareable(new FMyMediaInitializer());
    IModularFeatures::Get().RegisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::ModularFeatureName, MediaInitializer.Get());
}

void FMyCustomMediaPluginModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::ModularFeatureName, MediaInitializer.Get());
}

IMPLEMENT_MODULE(FMyCustomMediaPluginModule, MyCustomMediaPlugin)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `nDisplay` | 核心显示集群框架，提供此插件所服务的功能上下文 |
| `MediaFrameworkUtilities` | 提供媒体框架相关的工具和基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-26 | `3336c461` | [nDisplay] In-Camera VFX panel makes level dirty | 修复了 ICVFX 面板意外修改关卡数据的问题 |
| 2024-08-01 | `1dd0608a` | nDisplay: Propagate RadialOffset changes from LC level instance to ICVFX panel proxy. | 将灯光卡片实例的径向偏移变更同步到 ICVFX 面板代理 |
| 2024-05-15 | `8b89d9f4` | [nDisplay] Media tiles configuration dialog for ICVFX cameras | 为 ICVFX 摄影机添加了媒体分块配置对话框 |
| 2024-03-13 | `6491e949` | [nDisplay] Media configuration improvements | 对媒体配置功能进行了改进 |
| 2024-03-06 | `59d5a057` | [nDisplay] Fixed CIS validation issue where DisplayClusterModularFeaturesEditor artifacts have paths | 修复了构建系统中模块路径验证的问题 |

### 维护评价

- **状态**：**实验性但仍在维护**。插件标记为 `IsBetaVersion: true`，且并非默认启用，表明 Epic 认为其 API 或功能可能在未来版本中发生变化。
- **活跃度**：近期（2024-2025年）仍有持续的更新，主要是与 nDisplay 主线的 Media Tiles 和 ICVFX 面板功能协同进行 bug 修复和小幅改进。
- **建议**：该插件为深度 nDisplay 用户和媒体硬件集成商提供了必要的扩展能力。如果你需要集成第三方媒体流，使用此插件是官方推荐的方式。但请注意其“实验性”状态，应关注其接口在未来 Unreal 版本中的变更说明。对于不需要自定义媒体初始化的普通 nDisplay 用户，无需关注此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplayModularFeatures)
- 官方文档：无