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

Android 设备硬件种类繁多，不同 GPU/CPU/内存组合的性能差异巨大。这个插件解决的核心问题是：**如何在运行时自动识别 Android 设备的硬件规格，并选择最合适的 Device Profile（设备配置）**。

Device Profile 是 UE 中一组预设的画质/性能参数（如分辨率缩放、阴影质量、纹理质量等）。没有这个插件，所有 Android 设备只能使用同一个默认配置，导致高端设备浪费性能、低端设备帧率不足。

插件提供两个层面的能力：

1. **编辑器侧**：通过 ADB 连接的真机，自动探测硬件信息并生成 JSON 规格文件，这些文件同时用于 PIE 设备预览和设备配置匹配规则的编写。
2. **运行时侧**：在 Android 设备上运行时，根据硬件信息（GPU 型号、SoC、内存等）自动匹配并应用最佳 Device Profile。

## 使用场景

- 你的项目需要支持从低端到高端的多种 Android 设备 → 用此插件自动选择画质档位
- 你需要在编辑器中预览不同 Android 设备的表现 → 用 Commandlet 生成设备 JSON，再在 PIE 中选择预览设备
- 你需要根据 GPU 型号、芯片组等硬件特征自定义匹配规则 → 配合 `ConfigRules.txt` 使用

## 蓝图用法

此插件的核心逻辑在 C++ 层面完成设备检测和配置匹配，不暴露蓝图接口。Device Profile 的选择在引擎启动的极早期（`PostConfigInit`）自动完成，无需手动调用。

你可以在 **Project Settings → Platforms → Android → Device Profiles** 中配置匹配规则和对应的质量等级。

## C++ 用法

### 头文件引入

```cpp
#include "AndroidDeviceProfileCommandlets.h"
```

### 使用 Commandlet 生成设备预览数据

该 Commandlet 以无限循环方式运行，持续监听 ADB 连接的新设备，检测到新设备后自动生成 JSON 规格文件。

```cpp
// Commandlet 入口（通常通过命令行调用，无需直接编写 C++ 代码）
// 命令行用法：
// UnrealEditor-Cmd.exe MyProject.uproject -run=AndroidDeviceDetection.CreateAndroidPreviewDataFromADB -ConfigRules="Engine/Config/Android/ConfigRules.txt" -DeviceSpecsFolder="Engine/Content/Editor/PIEPreviewDeviceSpecs/Android"

// 如需在自定义工具中复用，可继承 UCreateAndroidPreviewDataFromADBCommandlet
// 来源: Private/CreateAndroidPreviewDataFromADBCommandlet.h
UCLASS()
class UMyAndroidDeviceScanner : public UCreateAndroidPreviewDataFromADBCommandlet
{
    GENERATED_BODY()
public:
    virtual int32 Main(const FString& Params) override
    {
        // 基类 Main 已包含完整的 ADB 设备发现和 JSON 生成逻辑
        return Super::Main(Params);
    }
};
```

### 运行时模块依赖

运行时模块 `AndroidDeviceProfileSelectorRuntime` 仅在 Android 平台加载（`PlatformAllowList: Android`），加载阶段为 `PostConfigInit`——这意味着它在引擎初始化的最早期就执行设备检测，在任何游戏代码运行之前就已经选好了 Device Profile。

## Demo 示例

此插件主要通过引擎内部机制工作，开发者通常不需要直接编写代码调用。典型的使用方式是：

**步骤 1**：通过 ADB 连接 Android 设备，运行 Commandlet 生成规格 JSON

```bash
# 在命令行执行（路径根据你的项目调整）
UnrealEditor-Cmd.exe MyProject.uproject ^
  -run=AndroidDeviceDetection.CreateAndroidPreviewDataFromADB ^
  -ConfigRules="Engine/Config/Android/ConfigRules.txt" ^
  -DeviceSpecsFolder="Engine/Content/Editor/PIEPreviewDeviceSpecs/Android"
```

**步骤 2**：在编辑器的 Device Profile 设置中，根据生成的 JSON 中的 GPU 型号、SoC 等信息编写匹配规则

**步骤 3**：打包后在 Android 设备上运行，运行时模块自动匹配并应用配置

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AndroidDeviceDetection` | Android 硬件检测库，负责通过 ADB/系统 API 获取设备的 GPU、SoC、内存等信息 |
| `PIEPreviewDeviceSpecification` | PIE（Play In Editor）设备预览规格，用于在编辑器中模拟不同 Android 设备 |

其余依赖（Json、JsonUtilities、RHI、ApplicationCore）均为引擎标准模块，无需额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏统一迁移至 UE_LOGF 格式 |
| 2026-03-02 | `f2f207d7` | [AndroidDeviceProfileSelectorRuntime] | 运行时模块的改动 |
| 2026-03-01 | `1d115ca4` | Changed codegen to only create one Z_Construct_<Type> function but with a bool as inparam to decide | 重构反射代码生成逻辑 |
| 2026-02-18 | `f5a10b68` | Add Preview json Versioning | 为预览 JSON 添加版本号支持 |
| 2026-02-13 | `bbbd7847` | Add ConfigRules to Android Preview Json | 预览 JSON 中新增 ConfigRules 字段 |

### 维护评价

该插件创建于 2014 年，是 UE 引擎的长期核心组件之一（约 12 年历史）。从近期提交记录来看，2026 年仍有持续的功能更新（JSON 版本化、ConfigRules 支持）和代码维护（日志宏迁移、代码生成重构），说明仍处于 **活跃维护** 状态。

作为 Epic 官方维护的 Android 平台核心支持插件，它是 Android 项目设备适配工作流中不可或缺的一环。**强烈推荐在所有面向 Android 的 UE 项目中启用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)（引擎级测试目录，未发现此插件独立测试）