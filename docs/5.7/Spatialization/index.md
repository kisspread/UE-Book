# Spatialization

> Plugin featuring a variety of basic audio spatialization solutions.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | 是（未设置 `EnabledByDefault: false`） |
| 包含内容 | 否 |
| 模块 | Spatialization (Runtime, PreDefault), SpatializationEditor (Editor, PostEngineInit) |
| 创建时间 | 2019-01-24 |
| 年龄标签 | 👴 老古董（~7年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Spatialization) | |

## 用途

Spatialization plugin 实现了一个**基于 ITD（Interaural Time Difference，双耳时间差）**的简易空间化算法。它模拟声音到达左右耳的时间差和强度差（ILD, Interaural Level Difference），从而在立体声输出中实现基本的 3D 定位效果。

核心原理：
- 根据声源相对听者的水平位置，计算声音到达左耳和右耳的距离差
- 利用延迟线（Delay Line）模拟时间差（ITD）
- 可选地通过增益差异模拟强度差（ILD）
- 支持基于距离的声像（Panning）强度曲线控制

这是一个轻量级的空间化方案，适合不需要完整 HRTF 的场景，或作为音频系统的基础参考实现。

## 使用场景

- 你需要一个简单快速的立体声空间化效果，不想集成第三方 HRTF 库
- 你在做原型开发或 Game Jam，需要即时可用的 3D 音频定位
- 你的目标平台性能有限，无法使用复杂的 HRTF 卷积
- 你想学习 UE5 音频空间化插件的实现方式，以此为参考编写自定义插件

## 蓝图用法

此 plugin 本身不暴露 BlueprintCallable 函数。它的配置通过**资产**（ITD Source Spatialization Settings）和**控制台变量**完成。

### 配置资产

在编辑器中，右键 Content Browser → Sounds → **ITD Source Spatialization Settings** 可创建设置资产：

| 属性 | 说明 |
|---|---|
| `bEnableILD` | 是否启用左右声道的强度差异（ILD） |
| `PanningIntensityOverDistance` | 声像强度随距离变化的曲线（Y 轴 0.0-1.0 对应 X 轴距离） |

将该资产赋给 Sound Source Component 的 **Spatialization Settings** 属性即可生效。

### 控制台变量

运行时可通过控制台调整参数：

| CVar | 默认值 | 说明 |
|---|---|---|
| `au.itd.SetSpeedOfSound` | 343.0 | 声速（米/秒） |
| `au.itd.SetHeadWidth` | 34.0 | 头部宽度（厘米），用于计算耳间距 |
| `au.itd.SetInterpolationTime` | 0.1 | 位置插值时间（秒），值越大跟踪越平滑 |
| `au.itd.EnableILD` | 1 | 是否启用 ILD（0=关闭, 1=开启） |

## C++ 用法

### 头文件引入

```cpp
#include "ITDSpatializer.h"
#include "ITDSpatializationSourceSettings.h"
```

### 核心类结构

Plugin 的架构分为三层：

1. **`FITDSpatializationPluginFactory`** — 工厂类，向 UE5 模块化特性系统注册空间化插件，暴露显示名称 "Simple ITD"，声明支持最多 2 通道输出
2. **`FITDSpatialization`** — 实现 `IAudioSpatialization` 接口，管理所有声源的 `FSourceSpatializer` 实例
3. **`FSourceSpatializer`** — 单个声源的空间化处理器，包含延迟线和增益计算逻辑

### 注册流程（模块启动时自动完成）

```cpp
// SpatializationModule.cpp — 模块启动时通过 ModularFeatures 注册工厂
void FSpatializationModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(
        FITDSpatializationPluginFactory::GetModularFeatureName(),
        &PluginFactory);
}
```

### 设置自定义声源参数（C++）

```cpp
// 创建 ITD 空间化设置对象
UITDSpatializationSourceSettings* Settings = NewObject<UITDSpatializationSourceSettings>();
Settings->bEnableILD = true;

// 配置声像强度曲线：近距离强 panning，远距离弱 panning
FRichCurve* Curve = Settings->PanningIntensityOverDistance.GetRichCurve();
Curve->AddKey(0.0f, 1.0f);    // 距离 0 时，panning 强度 100%
Curve->AddKey(500.0f, 0.5f);  // 距离 500 时，panning 强度 50%
Curve->AddKey(2000.0f, 0.0f); // 距离 2000 时，panning 强度 0%

// 将设置赋给 Audio Component
AudioComponent->SetSpatializationPluginSettings(Settings);
```

### 算法细节

ITD 延迟计算（源码 `ITDSpatializer.cpp`）：

```
HeadRadius = HeadWidth / 100.0 * 0.5  (转为米)
DistanceToLeftEar  = sqrt(X² + (HeadRadius + Y)²)
DistanceToRightEar = sqrt(X² + (HeadRadius - Y)²)
DeltaSeconds = (DistanceToLeftEar - DistanceToRightEar) / SpeedOfSound
```

ILD 增益计算基于声源 Y 轴位置的归一化值，再乘以距离曲线系数。

## Demo 示例

### 最小可编译示例

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "Engine",
    "AudioExtensions"  // 访问 IAudioSpatialization 接口
});
```

**使用 ITD 空间化设置（C++）：**

```cpp
// MySpatialTest.h
#pragma once
#include "CoreMinimal.h"
#include "Components/AudioComponent.h"
#include "ITDSpatializationSourceSettings.h"

class FMySpatialTest
{
public:
    void SetupSpatialAudio(UAudioComponent* AudioComp)
    {
        if (!AudioComp) return;

        // 创建 ITD 设置
        UITDSpatializationSourceSettings* Settings =
            NewObject<UITDSpatializationSourceSettings>();
        Settings->bEnableILD = true;

        // 配置 panning 强度随距离衰减
        FRuntimeFloatCurve& Curve = Settings->PanningIntensityOverDistance;
        FRichCurve* RichCurve = Curve.GetRichCurve();
        RichCurve->AddKey(0.0f, 1.0f);
        RichCurve->AddKey(1000.0f, 0.0f);

        // 应用设置（需要引擎已加载 Spatialization plugin）
        AudioComp->SetSpatializationPluginSettings(Settings);
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和模块管理 |
| `CoreUObject` | UObject 反射系统（用于 Settings 类） |
| `Engine` | 引擎核心（Audio Component 等） |
| `SignalProcessing` | 音频 DSP 工具（延迟线、指数缓动） |
| `AudioExtensions` | 音频插件接口（`IAudioSpatialization`、`IAudioSpatializationFactory`） |

Editor 模块额外依赖：`AudioEditor`、`UnrealEd`、`AudioMixer`、`LevelEditor`

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `a2e7518` | Added `UE_INLINE_GENERATED_CPP_BY_NAME` to source files | 自动化工具批量添加，非功能性改动 |
| 2025-04-23 | `93a1308` | Convert all files to use dllstorage on methods | DLL 导出符号规范化，编译系统调整 |
| 2023-01-16 | `bbc37aa` | IWYU updates to reduce includes | 头文件依赖清理，非功能性改动 |

### 维护评价

- **创建时间**：2019 年 1 月，已存在约 7 年
- **最近实质性更新**：最后一次功能性代码修改可以追溯到 2019 年前后；近三次提交全部是编译系统和代码规范的自动化批量修改
- **维护状态**：⚠️ **维护不活跃** — 代码功能层面已超过 6 年没有更新
- **推荐使用**：作为**学习参考**非常合适（代码简洁、结构清晰），但不建议用于生产环境。生产项目应考虑 UE5 内置的 HRTF 空间化或 MetaSounds 提供的空间化方案
- **注意**：此 plugin 最大支持 **2 通道立体声**输出，不支持环绕声

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Spatialization)
- [IAudioSpatialization 接口定义](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/AudioExtensions/Source/AudioExtensions/Public/IAudioExtensionPlugin.h)
