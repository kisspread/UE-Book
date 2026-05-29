# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器应用 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `CaptureManagerEditor` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是虚幻引擎虚拟制片工作流中的数据采集管理工具。它提供了一整套从硬件设备端采集数据、转码处理、并上传至 UE 进行导入的完整管线。具体能力包括：

- **设备控制与监控**：连接并管理各类捕获设备（如 Live Link 设备），实时监控设备状态
- **数据获取与转码**：从捕获设备获取原始数据，进行格式转换和编码处理（支持自动旋转、第三方编码器等）
- **数据上传与导入**：将处理后的数据通过 Unreal Endpoint 传输到引擎内，供后续资产导入使用
- **Live Link 集成**：通过 Live Link 协议实时接收设备数据流，支持自定义设备能力扩展

该插件解决的核心问题是：在虚拟制片场景中，如何标准化地管理多种捕获设备的数据采集全流程，从"拿数据"到"数据进引擎"的端到端自动化。

## 使用场景

- 你在进行虚拟制片拍摄，需要从专业捕获设备（如动作捕捉、面部捕捉等）实时获取数据并导入 UE → 使用 CaptureManagerApp
- 你需要为自定义硬件设备开发 Live Link 数据源插件 → 参考 `ExampleLiveLinkDevices` 和 `IngestLiveLinkDevice` 模块
- 你需要在项目中配置捕获管理器的默认行为（编码格式、旋转模式等）→ 通过 `CaptureManagerSettings` 模块
- 你需要在其他主机或进程中接收捕获数据 → 使用 `CaptureManagerUnrealEndpoint` 模块

## 模块概览

| 模块 | 说明 |
|---|---|
| `CaptureManagerEditor` | 捕获管理器的主编辑器模块，提供设备管理 UI、数据采集流程控制和状态监控界面 |
| `CaptureManagerSettings` | 捕获管理器的配置系统，管理编码器设置、旋转模式、第三方编码器等参数 |
| `CaptureManagerUnrealEndpoint` | Unreal 端数据接收端点，负责接收从捕获设备传输过来的数据并在引擎内进行处理 |
| `ExampleLiveLinkDevices` | 示例 Live Link 设备实现，展示了如何为自定义捕获硬件开发 Live Link 数据源 |
| `IngestLiveLinkDevice` | 数据摄入 Live Link 设备模块，将捕获设备数据通过 Live Link 协议接入 UE 并触发导入流程 |
| `LiveLinkCapabilities` | Live Link 能力扩展模块，为 Live Link 设备提供额外的功能声明和处理能力 |

## 蓝图用法

> 各模块的详细蓝图 API 请参阅对应的子模块文档。

本插件主要用于编辑器端工作流控制，核心功能通过编辑器 UI 面板操作，蓝图可访问的节点较少。如需在蓝图中集成捕获管理功能，请参考各模块文档中列出的 `UFUNCTION(BlueprintCallable)` 接口。

## C++ 用法

> 详细的 C++ API 请参阅各子模块文档。以下为入口概览。

### 模块头文件引入

```cpp
#include "CaptureManagerEditorModule.h"        // 主编辑器模块
#include "CaptureManagerSettings.h"             // 配置管理
#include "CaptureManagerUnrealEndpointModule.h" // 数据端点
```

### 典型使用流程

```cpp
// 1. 通过编辑器模块启动捕获管理器
ICaptureManagerEditorModule& EditorModule = FModuleManager::Get().LoadModuleChecked<ICaptureManagerEditorModule>("CaptureManagerEditor");

// 2. 通过 Settings 模块获取/修改捕获配置
// 3. UnrealEndpoint 负责接收和处理数据传输
```

## Demo 示例

`ExampleLiveLinkDevices` 模块本身即为示例代码，展示了如何创建自定义 Live Link 捕获设备。详见子模块文档。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | LiveLinkCapabilities 模块依赖，用于编辑器端能力声明 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 在 CaptureManagerCore 中新增 CPS 客户端模块 |
| 2026-04-28 | `6eba47f3` | [Capture Manager] Warn when Third Party Encoder is required for ingest | 摄入数据需要第三方编码器时增加警告提示 |
| 2026-04-23 | `43d97726` | MediaProfile: Moved UMediaProfile and related entities to its own plugin to avoid dependency on Open | MediaProfile 拆分为独立插件以减少依赖 |
| 2026-04-20 | `a8e2df25` | [CaptureManager] Add auto-rotation mode to ECaptureManagerRotation | 为捕获管理器旋转枚举新增自动旋转模式 |
| 2026-04-16 | `cf2dffa4` | [CaptureManager] Fix broken LLH encoder defaults. | 修复 LLH 编码器默认值配置错误 |

### 维护评价

- **活跃维护** ✅：近 2 周内持续有功能性更新（编码器支持、旋转模式、模块拆分等）
- 创建于 2025 年 2 月，是较新的虚拟制片工具链组件
- 持续有新功能迭代（CPS 客户端、自动旋转、第三方编码器支持）
- 作为 VP 管线核心组件，预计将持续维护
- **推荐使用**：如果你的项目涉及虚拟制片数据采集工作流，这是一个由 Epic 官方维护的成熟解决方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Tests)