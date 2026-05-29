# Location Services IOS Implementation

> IOS implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 中文名 | iOS定位服务 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LocationServicesIOSEditor` (Editor), `LocationServicesIOSImpl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesIOSImpl) | |

## 用途

这个插件是 iOS 平台的定位服务实现层，为 `LocationServicesBPLibrary` 插件提供 iOS 端的底层绑定。它封装了 Apple 的 CoreLocation 框架，使得蓝图能够通过统一接口获取 iOS 设备的 GPS 位置数据（经纬度、精度、速度等）。

插件本身不定义蓝图接口，而是作为平台特定实现，通过 LocationServicesBPLibrary 定义的抽象接口为 iOS 设备提供定位能力。这是 UE 跨平台定位服务架构中的 iOS 一环（对应 Android 平台有类似实现）。

## 使用场景

- 你在开发基于地理位置的 iOS 应用（如 AR 地图游戏、附近的人功能）→ 需要此插件
- 你的 UE 项目需要访问 iOS 设备的 GPS 数据 → 启用此插件并配合 LocationServicesBPLibrary 使用
- 你需要在蓝图中请求设备位置权限并获取坐标 → 使用 LocationServicesBPLibrary 的蓝图节点（此插件提供底层实现）

## 蓝图用法

本插件的 Runtime 模块作为 LocationServicesBPLibrary 的平台实现层，不直接暴露额外蓝图节点。蓝图交互通过 LocationServicesBPLibrary 插件完成。

编辑器模块提供的设置项会在 iOS 平台的项目设置中出现：

### 项目设置（iOS 定位权限文本）

| 设置项 | 说明 | 所在类 |
|---|---|---|
| Location Services Always Use Permission Text | 请求"始终允许"定位权限时显示给用户的说明文本 | `ULocationServicesIOSSettings` |
| Location Services In-Use Permission Text | 请求"使用期间允许"定位权限时显示给用户的说明文本 | `ULocationServicesIOSSettings` |

这些文本会写入 iOS App 的 `Info.plist`，对应 `NSLocationAlwaysUsageDescription` 和 `NSLocationWhenInUseUsageDescription` 键。如果这些字段为空，iOS 会拒绝应用的定位权限请求。

### 使用示例

1. 在 **项目设置 → Plugins → Location Services** 中填写 iOS 定位权限说明文本
2. 在蓝图中使用 LocationServicesBPLibrary 提供的节点（如 `GetLocationServicesImpl`、`CheckLocationAvailability` 等）
3. 在 iOS 设备上运行时，系统会弹出权限请求对话框，显示你配置的说明文本

## C++ 用法

### 头文件引入

```cpp
#include "LocationServicesIOSEditor.h"
```

### 基本用法 - 配置 iOS 定位权限文本

```cpp
// 获取 iOS 定位服务设置（可在 C++ 中动态设置，也可通过项目设置 UI 配置）
ULocationServicesIOSSettings* Settings = GetMutableDefault<ULocationServicesIOSSettings>();
Settings->LocationAlwaysUsageDescription = TEXT("我们需要您的位置来提供基于位置的游戏体验");
Settings->LocationWhenInUseDescription = TEXT("仅在使用应用时访问您的位置");
Settings->SaveConfig();
```

### 进阶用法 - 运行时获取位置

Runtime 模块的实现对使用者透明。在 C++ 中应通过 LocationServicesBPLibrary 的接口使用：

```cpp
#include "LocationServicesBPLibrary.h"

// 检查定位服务是否可用
bool bAvailable = ULocationServicesBPLibrary::CheckLocationAvailability();

// 开始位置更新
ULocationServicesBPLibrary::StartLocationService();

// 获取当前位置
FLocationServicesData CurrentLocation = ULocationServicesBPLibrary::GetLastKnownLocation();
// CurrentLocation 包含 Latitude, Longitude, Timestamp, HorizontalAccuracy, VerticalAccuracy, Speed 等字段
```

## Demo 示例

本插件主要是配置和平台实现，最小集成示例：

```cpp
// MyGameModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyGameModule.cpp
#include "MyGameModule.h"
#include "LocationServicesIOSSettings.h"

void FMyGameModule::StartupModule()
{
    // 配置 iOS 定位权限说明文本
    ULocationServicesIOSSettings* Settings = GetMutableDefault<ULocationServicesIOSSettings>();
    if (Settings)
    {
        Settings->LocationAlwaysUsageDescription = 
            TEXT("Allow this app to access your location for gameplay features.");
        Settings->LocationWhenInUseDescription = 
            TEXT("Allow this app to access your location while you are playing.");
        Settings->SaveConfig();
    }
}

void FMyGameModule::ShutdownModule()
{
    // 清理
}

IMPLEMENT_MODULE(FMyGameModule, MyGame)
```

## 模块依赖

本插件依赖 `LocationServicesBPLibrary` 插件（在 .uplugin 中声明）。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 格式化宏 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复 iOS 大小写敏感文件系统下的头文件引用问题 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复 iOS 持续集成构建问题 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量更新 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的供应商链接更新为 HTTPS |

### 维护评价

此插件创建于 2016 年，是 UE4 移动端定位服务的基础组件。最近的更新（2026 年初）主要是编译维护性修复（日志宏迁移、头文件大小写修复），而非功能性更新。自 2022 年以来没有实质性功能变更，说明该插件功能已经稳定成熟。

**注意**：此插件 `EnabledByDefault=false`，需要手动在插件管理器中启用。作为 iOS 平台特定实现，仅在 iOS 目标平台上有意义。

**推荐使用**：如果你的 iOS 项目需要定位功能，此插件是必需的（配合 LocationServicesBPLibrary）。它功能稳定，维护性更新正常，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesIOSImpl)
- [LocationServicesBPLibrary 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesBPLibrary)（跨平台蓝图接口层）