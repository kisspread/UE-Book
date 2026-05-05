# MetaHuman SDK

> Utilities and tools for working with MetaHumans in Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、本地化资源） |
| 模块 | `MetaHumanSDKRuntime` (Runtime), `MetaHumanSDKEditor` (Editor), `InterchangeDNA` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK) | |

## 概述

MetaHuman SDK 是 Epic 官方提供的 MetaHuman 角色完整工具链，覆盖从 DNA 数据导入到运行时动画驱动的全流程。插件由三个模块组成：

| 模块 | 类型 | 职责 |
|---|---|---|
| [MetaHumanSDKRuntime](./MetaHumanSDKRuntime.md) | Runtime | 运行时驱动 MetaHuman 的面部和身体动画——通过 `UMetaHumanComponentUE` 组件自动配置 Rig Logic、Control Rig、物理资产和 LOD 阈值 |
| [MetaHumanSDKEditor](./MetaHumanSDKEditor.md) | Editor | 编辑器工具链——MetaHuman 导入、资产验证、打包归档（`.mharchive`）、云服务集成（Auto-Rig / 纹理合成） |
| [InterchangeDNA](./InterchangeDNA.md) | Editor | DNA 导入桥梁——将 `.dna` 文件通过 Interchange 框架翻译为 SkeletalMesh、MorphTarget 等引擎资产 |

## 架构关系

```
.dna 文件
   │
   ▼
┌──────────────┐     Interchange 节点树      ┌─────────────────┐
│ InterchangeDNA │ ──────────────────────────▶ │ SkeletalMesh    │
│ (翻译器)       │                              │ + MorphTarget   │
└──────────────┘                              │ + Skeleton      │
                                               └────────┬────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ MetaHumanSDKEditor │
                                              │ (导入/验证/打包)    │
                                              └────────┬────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ MetaHumanSDKRuntime │
                                              │ (运行时动画驱动)    │
                                              └─────────────────┘
```

**数据流**：MetaHuman Creator → `.dna` 文件 → InterchangeDNA 翻译为 SkeletalMesh → Editor 模块管理导入/验证/打包 → Runtime 模块在运行时驱动动画。

## 核心类速查

| 类名 | 模块 | 用途 |
|---|---|---|
| `UMetaHumanComponentUE` | Runtime | 运行时组件，自动配置 MetaHuman 角色的动画管道 |
| `UMetaHumanComponentBase` | Runtime | 组件基类，提供 LOD 阈值、Control Rig、物理资产配置 |
| `FMetaHumanImport` | Editor | MetaHuman 导入器（Quixel Bridge / 本地 zip） |
| `UMetaHumanAssetManager` | Editor | 资产发现、依赖管理、打包归档 |
| `UMetaHumanVerificationRuleCollection` | Editor | 可扩展验证规则系统 |
| `UMetaHumanAssetReport` | Editor | 验证报告（HTML/JSON/纯文本） |
| `FAutoRigServiceRequest` | Editor | 云端 Auto-Rig 服务请求 |
| `FInterchangeDnaModule` | InterchangeDNA | DNA 同步导入接口（`ImportSync()`） |
| `UMetaHumanInterchangeDnaTranslator` | InterchangeDNA | DNA → Interchange 节点树翻译器 |

## 快速上手

### 1. 导入 MetaHuman

从 Quixel Bridge 自动导入，或通过 C++ 手动导入：

```cpp
#include "Import/MetaHumanImport.h"

auto Importer = UE::MetaHuman::FMetaHumanImport::Get();
FMetaHumanImportDescription ImportDesc;
ImportDesc.CharacterName = TEXT("MyMetaHuman");
ImportDesc.DestinationPath = TEXT("/Game/MetaHumans");
TOptional<UObject*> Result = Importer->ImportMetaHuman(ImportDesc);
```

### 2. 验证资产

```cpp
#include "Verification/MetaHumanVerificationRuleCollection.h"
#include "Verification/VerifyMetaHumanGroom.h"

UMetaHumanAssetReport* Report = NewObject<UMetaHumanAssetReport>();
auto* Rules = NewObject<UMetaHumanVerificationRuleCollection>();
Rules->AddVerificationRule(NewObject<UVerifyMetaHumanGroom>());
Rules->ApplyAllRules(MyAsset, Report, Options);
```

### 3. 运行时驱动动画

在 MetaHuman Actor 上添加 `UMetaHumanComponentUE` 组件即可——组件在 BeginPlay 时自动配置所有身体部位的后处理 AnimBP、Control Rig、Rig Logic LOD 阈值和物理资产。

### 4. 程序化导入 DNA

```cpp
#include "InterchangeDnaModule.h"
#include "DNAUtils.h"

FInterchangeDnaModule& Module = FInterchangeDnaModule::GetModule();
TSharedPtr<IDNAReader> Reader = ReadDNAFromBuffer(&DNAData, EDNADataLayer::All);
USkeletalMesh* Mesh = Module.ImportSync("Face", "/Game/Face", Reader);
Module.SetSkelMeshDNAData(Mesh, Reader);
```

## 模块依赖汇总

**使用者需要引用的公共模块**：

| 模块 | 用于 |
|---|---|
| `MetaHumanSDKRuntime` | 运行时组件和类型定义 |
| `MetaHumanSDKEditor` | 编辑器工具（导入、验证、打包） |
| `InterchangeDNA` | DNA 文件导入 |
| `Core` / `CoreUObject` / `Engine` | UE 基础设施 |

**插件级依赖**：ControlRig、RigLogic、HairStrands

## 维护状态

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-10 | `9585d26c` | 为包含 VT 或 Substrate 材质的 MetaHuman 包添加验证警告 |
| 2025-10-03 | `15c2d59e` | 检测与用户项目设置不兼容的引擎特性 |
| 2025-10-01 | `b35afec6` | 修复阿拉伯语本地化问题 |
| 2025-08-01 | `4d797bcdc6b4` | DLL 导出宏批量修正（InterchangeDNA） |
| 2025-07-31 | `0f2260027766` | 统一各插件的 Interchange 使用方式 |

**综合评价**：
- **活跃维护**：2025 年 4 月创建，近期（2025 年 10 月）仍有功能性更新
- 更新聚焦于资产兼容性检测和跨项目打包流程改进
- 作为 MetaHuman 产品线的核心 SDK，将持续随 MetaHuman 迭代演进
- **推荐使用**：✅ 使用 MetaHuman 角色的项目必需此插件

## 子模块文档

- [MetaHumanSDKRuntime](./MetaHumanSDKRuntime.md) — 运行时动画驱动
- [MetaHumanSDKEditor](./MetaHumanSDKEditor.md) — 编辑器工具链
- [InterchangeDNA](./InterchangeDNA.md) — DNA 导入翻译层

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/MetaHumanSDKEditor/Private/Tests)
