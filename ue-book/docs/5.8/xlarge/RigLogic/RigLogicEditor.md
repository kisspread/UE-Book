# RigLogic Plugin

> RigLogic Plugin for Facial Animation

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画驱动 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DNA 面部动画资产、缩略图资源、MetaHuman 相关蓝图资产） |
| 模块 | `RigLogicDeveloper` (Runtime), `RigLogicEditor` (Runtime), `RigLogicLib` (Runtime), `RigLogicLibTest` (Runtime), `RigLogicModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic) | |

---

## 用途

RigLogic 是 Unreal Engine 面部动画系统的核心驱动插件，负责将 **DNA 文件**中描述的面部骨骼、混合形状（Blend Shapes）和动画映射（Animated Maps）转换为可运行时驱动的面部动画数据。

DNA 文件是 MetaHuman Creator / MetaHuman Animator 等外部工具输出的标准化面部数据格式，包含面部拓扑、关节层级、混合形状权重、RBF 权重等全部信息。RigLogic 插件解决的核心问题是：

1. **DNA 导入与转换**：将 DNA 文件解析为 `UDNA` 资产，附加到 `USkeletalMesh` 上
2. **运行时驱动**：通过 `AnimNode_RigLogic` 在运行时根据输入控制属性（Control Attributes）计算面部关节变换和混合形状权重
3. **高性能计算**：核心计算库支持 Scalar、SSE、AVX、NEON 四种后端，按平台自动选择最优 SIMD 指令集
4. **LOD 管理**：支持按平台配置面部动画的最高/最低 LOD 级别，优化移动端性能

该插件本质上是 MetaHuman 系统的"引擎侧执行器"——MetaHuman Creator 负责创作，RigLogic 负责在 UE 里运行。

---

## 使用场景

- 你使用 **MetaHuman Creator** 创建了数字人角色 → 用 RigLogic 导入 DNA 并驱动面部动画
- 你使用 **MetaHuman Animator** 从视频捕捉了面部表演 → 用 RigLogic 将捕捉数据应用到 MetaHuman 角色上
- 你需要为自定义角色支持 **DNA 格式的面部驱动** → 用 RigLogic 将 DNA 文件绑定到自定义骨骼网格
- 你需要将旧版 DNA Asset UserData **迁移到独立 DNA 资产** → 用 `ConvertLegacyDNAAssetsCommandlet` 批量转换
- 你需要按平台优化面部动画性能 → 在 `Project Settings > Plugins > RigLogic` 中配置 LOD 和计算后端

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import And Attach DNA` | 将 DNA 文件导入并附加到指定骨骼网格资产 | `UDNAImporterLibrary` |
| `Import Skeletal Mesh DNA File` | （已废弃）导入 DNA 文件到骨骼网格 | `UDNAImporterLibrary` |

### 使用示例（蓝图描述）

**自动导入 DNA 文件**：

1. 在蓝图中添加 `Import And Attach DNA` 节点（分类：`DNA`）
2. 连接 DNA 文件路径字符串（如 `C:\MetaHumans\MyCharacter.dna`）
3. 连接目标 `USkeletalMesh` 资产引用
4. 设置 `bReplaceExisting` 为 `true` 可替换已有 DNA 数据，`false` 仅附加新数据
5. 执行后 DNA 数据会自动附加到骨骼网格上，`AnimNode_RigLogic` 即可驱动面部动画

> **注意**：旧的 `ImportSkeletalMeshDNA` 函数已在 UE 5.8 中废弃，请迁移到 `ImportAndAttachDNA`。

---

## C++ 用法

### 头文件引入

```cpp
#include "DNAImporter.h"
#include "DNAImporterLibrary.h"
```

### 基本用法：程序化导入 DNA 文件

从 `DNAImporter` 类提取：

```cpp
#include "DNAImporter.h"

// 通过文件对话框交互式导入 DNA（编辑器工具用）
UDNAImporter* Importer = NewObject<UDNAImporter>();
TArray<USkeletalMesh*> Meshes = { MySkeletalMesh };
UDNA* ImportedDNA = Importer->ImportDNAWithPrompt(Meshes);

// 自动化导入（管线 / 命令行用）
bool bSuccess = Importer->ImportDNAAutomated(
    TEXT("/Path/to/character.dna"),
    MySkeletalMesh,
    /*bReplaceExisting=*/ true
);
```

### 进阶用法：从旧版 Asset UserData 迁移

```cpp
// 将旧版 UDNAAsset（作为 AssetUserData 附加在 SkeletalMesh 上）迁移到独立 UDNA 资产
UDNAImporter* Importer = NewObject<UDNAImporter>();
bool bConverted = Importer->ConvertFromLegacyAssetUserData(MySkeletalMesh);
```

### 进阶用法：DNA 导出

```cpp
UDNAImporter* Importer = NewObject<UDNAImporter>();
// 交互式导出（弹出文件夹选择对话框）
Importer->ExportDNAWithPrompt(MyDNAToExport);

// 自动化导出到指定目录
Importer->ExportDNA(MyDNAToExport, TEXT("/Game/ExportedDNA/"));
```

### 进阶用法：配置导入默认值

在 C++ 中读取/设置项目级 DNA 导入配置：

```cpp
#include "DNAImportSettings.h"

// 获取项目设置单例
const UDNAImportSettings* Settings = GetDefault<UDNAImportSettings>();

// 读取默认 LOD 配置
const FDNAConfig& LODConfig = Settings->DefaultDNAConfig;

// 读取默认 RigLogic 计算配置（后端、精度、线程等）
const FRigLogicConfiguration& RigConfig = Settings->DefaultRigLogicConfiguration;
```

---

## Demo 示例

```cpp
// MyDNAImportTool.h
#pragma once

#include "CoreMinimal.h"
#include "DNAImporter.h"
#include "UDNA.h"

class FMyDNAImportTool
{
public:
    /** 从指定路径导入 DNA 文件并附加到骨骼网格 */
    static bool ImportDNAForMesh(const FString& DNAFilePath, USkeletalMesh* TargetMesh)
    {
        if (!TargetMesh)
        {
            UE_LOG(LogTemp, Error, TEXT("TargetMesh is null"));
            return false;
        }

        UDNAImporter* Importer = NewObject<UDNAImporter>();
        return Importer->ImportDNAAutomated(DNAFilePath, TargetMesh, /*bReplaceExisting=*/ true);
    }

    /** 批量重新导入场景中所有已附加 DNA 的骨骼网格 */
    static void ReimportAllDNAAssets(const TArray<UDNA*>& DNAAssets)
    {
        UDNAImporter* Importer = NewObject<UDNAImporter>();
        for (UDNA* DNA : DNAAssets)
        {
            if (DNA)
            {
                Importer->ReimportDNA(DNA);
            }
        }
    }
};
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MessageLog` | 导入/转换过程中的消息日志输出 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具函数（LOD、导入辅助） |
| `RHI` / `RenderCore` | 渲染硬件接口，用于 LOD 和平台相关配置 |
| `AssetRegistry` | DNA 资产注册与标签管理 |
| `EditorFramework` | 编辑器框架支持（工厂、资产定义） |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `de0806c7` | Fix RigLogic NaN output from TwistSwing/RBF when ControlAttributeCurves overwrites driver-joint quat | 修复控制属性曲线覆盖驱动关节四元数时输出 NaN 的问题 |
| 2026-05-13 | `52da7ee0` | Fix quaternion joints evaluator test in case no rotation support is compiled in for the zyx sequence | 修复 ZYX 旋转序列未编译时四元数关节评估器测试失败 |
| 2026-05-13 | `27f94d1b` | Fix RigLogic ML Joints initialization of rotation adapter in the absence of coordinate system conver | 修复缺少坐标系转换时 ML 关节旋转适配器的初始化 |
| 2026-05-13 | `4b5d4e7d` | Notify dependent AnimNode_RigLogic instances when RigRuntimeContext is reinitialized due to config c | 配置变更导致运行时上下文重新初始化时通知依赖的 AnimNode 实例 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为三种 RigLogic 运行时集成实现统一的集成测试 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2020 年 7 月，从内部 Dev-CharacterTech 分支集成到 UE5
- **最近更新**：2026 年 5 月持续有功能性修复和测试完善（四元数 NaN、坐标系转换、ML 关节初始化等）
- **维护质量**：近期提交集中在数学精度修复和运行时稳定性提升，说明核心计算引擎仍在积极优化
- **已知趋势**：部分旧版 API（如 `ImportSkeletalMeshDNA`、`DNAAssetImportUI`）已在 UE 5.8 中标记为废弃，正在简化导入流程
- **推荐程度**：**强烈推荐**。作为 MetaHuman 系统的运行时核心，该插件是 Epic 官方重点维护的项目，适合作为面部动画管线的基础设施

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)
- [DNA 导入设置](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicEditor/Public/DNAImportSettings.h)
- [DNA 导入库（蓝图可调用）](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicEditor/Public/DNAImporterLibrary.h)
- [DNA 导入器（C++ API）](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicEditor/Public/DNAImporter.h)
- [旧版资产迁移命令行工具](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicEditor/Public/Commandlets/ConvertLegacyDNAAssetsCommandlet.h)