# Android Device Profile Selector

> Android Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 中文名 | 安卓设备配置选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidDeviceProfileSelector` (Editor), `AndroidDeviceProfileCommandlets` (Editor), `AndroidDeviceProfileSelectorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector) | |

## 用途

该插件在运行时根据当前 Android 设备的硬件特征（如 GPU 型号、CPU 架构、厂商、机型等）自动匹配并应用最合适的设备配置文件（Device Profile）。它解决的核心问题是：Android 设备碎片化严重，不同硬件性能差异巨大，需要根据具体设备自动选择最佳渲染和性能配置，而不是对所有设备使用同一套默认设置。

插件实现了 `IDeviceProfileSelectorModule` 接口，在引擎启动阶段（`PostConfigInit`）介入，通过查询设备的 GPU、制造商、型号等属性，从预定义的设备配置规则中找到最匹配的 Profile，并将其应用到当前运行环境。此外还包含特定硬件的 workaround 处理，例如针对某些需要 Java SurfaceView 缩放修复的设备。

## 使用场景

- 你开发了一款 Android 游戏，需要在高端旗舰机上启用高画质、在低端机型上自动降级画质 → 使用此插件自动选择对应 Device Profile
- 你需要为特定厂商（如三星、华为、小米）的设备设置专门的渲染优化 → 在 Device Profile 规则中配置匹配条件
- 你的 Android 项目需要根据 GPU 型号（如 Adreno、Mali、PowerVR）自动切换材质质量 → 插件的运行时模块会在启动时自动匹配
- 你需要检测并处理特定 Android 设备的已知兼容性问题（如 SurfaceView 缩放 bug）→ 插件内置了硬件 workaround 检查

## 蓝图用法

该插件主要在引擎启动时自动工作，不提供 BlueprintCallable 节点。设备配置选择是通过模块注册机制实现的，用户通过编辑 Device Profile 配置文件（DefaultDeviceProfiles.ini 等）来定义匹配规则。

如果需要在运行时查询当前设备的配置信息，可以通过控制台变量（CVar）或编辑器中的 Device Profile 面板查看当前应用的配置。

## C++ 用法

### 头文件引入

```cpp
#include "IDeviceProfileSelectorModule.h"
```

### 基本用法

该插件的核心逻辑封装在运行时模块中，通常不需要直接调用。引擎会在启动时自动加载并执行设备选择逻辑。以下是接口的关键方法签名：

```cpp
// 获取运行时设备配置名（由插件自动调用）
virtual const FString GetRuntimeDeviceProfileName() override;

// 查询设备选择器属性值
virtual bool GetSelectorPropertyValue(const FName& PropertyType, FString& PropertyValueOUT) override;
```

### 进阶用法

如果需要自定义设备选择逻辑或扩展设备检测能力，可以参考该插件实现 `IDeviceProfileSelectorModule` 接口：

```cpp
// 参考 AndroidDeviceProfileSelectorRuntimeModule.h 的实现模式
class FMyDeviceProfileSelectorModule : public IDeviceProfileSelectorModule
{
public:
    virtual const FString GetRuntimeDeviceProfileName() override
    {
        // 根据设备硬件信息返回最匹配的配置名
        // Android 插件内部会查询 GPU、制造商、型号等信息进行匹配
        return TEXT("MyDeviceProfile");
    }

    virtual bool GetSelectorPropertyValue(const FName& PropertyType, FString& PropertyValueOUT) override
    {
        // 返回特定属性值，如 GPU 型号、设备制造商等
        return false;
    }

    virtual void StartupModule() override { }
    virtual void ShutdownModule() override { }
};
```

## Demo 示例

该插件是引擎内部使用的自动化模块，不建议直接在游戏代码中使用其 API。正确的使用方式是配置 Device Profile 规则文件。

典型的配置方式（`DefaultDeviceProfiles.ini`）：

```ini
[Android DeviceProfile +DeviceProfileName=SamsungGalaxy]
+MatchedProfiles=Android
+MatchedProperties=DeviceMake:Samsung
+MatchedProperties=DeviceModel:SM-G*

[Android_Low DeviceProfile]
DeviceType=Android
BaseProfileName=
+CVars=r.MobileContentScaleFactor=0.7
+CVars=r.MobileMSAA=2
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AndroidDeviceDetection` | Android 设备硬件信息检测（GPU、CPU、制造商、型号等） |
| `PIEPreviewDeviceSpecification` | PIE 预览设备规格定义，用于编辑器中模拟特定设备 |
| `Json` / `JsonUtilities` | 解析设备配置的 JSON 规则文件 |
| `RHI` | 渲染硬件接口，用于查询 GPU 相关信息 |
| `ApplicationCore` | 应用核心层，获取设备基本信息 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-03-02 | `f2f207d7` | [AndroidDeviceProfileSelectorRuntime] | 运行时模块改动 |
| 2026-03-01 | `1d115ca4` | Changed codegen to only create one Z_Construct_<Type> function but with a bool as inparam to decide | 优化代码生成，减少冗余的 Z_Construct 函数 |
| 2026-02-18 | `f5a10b68` | Add Preview json Versioning | 为预览设备 JSON 添加版本控制 |
| 2026-02-13 | `bbbd7847` | Add ConfigRules to Android Preview Json | 向 Android 预览 JSON 添加配置规则 |

### 维护评价

- **活跃维护**：最近 6 个月内持续有功能性更新，包括日志系统迁移、代码生成优化、JSON 规则版本控制等
- 作为 UE 从创立之初就存在的核心 Android 支持插件（2014 年），已经持续维护超过 12 年
- 属于引擎基础设施级组件，随引擎版本同步更新，稳定性有保障
- 推荐在所有 Android 项目中使用，它能自动根据设备硬件优化配置，无需手动干预

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector)
- [运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector/Source/AndroidDeviceProfileSelectorRuntime)
- [编辑器模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector/Source/AndroidDeviceProfileSelector)