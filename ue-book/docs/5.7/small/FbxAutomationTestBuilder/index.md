# FbxAutomationTestBuilder

> 

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | FbxAutomationTestBuilder (Editor) |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/FbxAutomationTestBuilder) | |

## 用途

FbxAutomationTestBuilder 是一个**编辑器内可视化工具**，用于创建 FBX 导入自动化测试的测试计划（Test Plan），并将其保存为 JSON 文件。

UE5 的 FBX 导入管线支持通过自动化测试验证导入结果的正确性（测试入口在 `Editor.Import.Fbx`）。要运行这些测试，需要为每个 FBX 文件准备一个同名的 `.json` 文件，其中包含：
- 导入选项（`UFbxImportUI` 的各种设置）
- 预期结果（顶点数、材质数、LOD 数量、骨骼位置、动画关键帧等）

手动编写这些 JSON 非常繁琐且容易出错。FbxAutomationTestBuilder 提供了一个 Slate UI 窗口，让你能：
1. 从配置的测试目录中选择 FBX 文件
2. 创建和编辑多个测试计划（Test Plan）
3. 通过 Details 面板可视化配置 `UFbxImportUI` 的所有导入选项
4. 设置每个测试计划的预期结果验证条件
5. 将所有计划保存为与 FBX 文件同名的 `.json` 文件

**注意**：此插件默认不启用（`EnabledByDefault: false`），需要在编辑器设置中手动启用。

## 使用场景

- 你正在开发或维护 FBX 导入功能，需要验证导入结果是否正确 → 用此工具创建测试计划
- 你的项目需要对特定 FBX 资产的导入结果做回归测试 → 创建包含精确预期结果的测试计划
- 你需要测试 FBX 的 Re-import、LOD 添加、备用蒙皮等功能 → 使用不同的 `EFBXTestPlanActionType`
- 你需要批量验证大量 FBX 文件的导入结果 → 先用此工具为每个 FBX 创建 JSON，然后运行 `Editor.Import.Fbx` 自动化测试

## 蓝图用法

此插件**没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。它是一个纯编辑器 UI 工具，通过编辑器菜单使用，不提供蓝图接口。

## C++ 用法

### 头文件引入

```cpp
// 测试计划的数据结构和序列化 API
#include "Tests/FbxAutomationCommon.h"
```

### 核心数据结构

`FbxAutomationCommon.h` 定义了测试计划的核心类型：

```cpp
// 来源: Engine/Source/Editor/UnrealEd/Public/Tests/FbxAutomationCommon.h

// 测试计划的动作类型
UENUM()
enum EFBXTestPlanActionType : int
{
    Import,              // 普通导入
    Reimport,            // 重新导入（需要先执行 Import）
    AddLOD,              // 添加新 LOD
    ReimportLOD,         // 重新导入已有 LOD
    ImportReload,        // 导入后保存、删除内存、重新加载，测试持久化
    AddAlternateSkinnig, // 添加备用蒙皮（需要 _alt 后缀文件）
};

// 预期结果的预设类型
UENUM()
enum EFBXExpectedResultPreset : int
{
    Error_Number,                      // 预期错误数量 [int0]
    Warning_Number,                    // 预期警告数量 [int0]
    Created_Staticmesh_Number,         // 预期创建的静态网格数 [int0]
    Created_Skeletalmesh_Number,       // 预期创建的骨骼网格数 [int0]
    Materials_Created_Number,          // 预期创建的材质数 [int0]
    Material_Slot_Imported_Name,       // 材质槽导入名 [int0=槽索引, string0=预期名]
    Vertex_Number,                     // 所有 LOD 总顶点数 [int0]
    Lod_Number,                        // 预期 LOD 数量 [int0]
    Vertex_Number_Lod,                 // 特定 LOD 顶点数 [int0=LOD索引, int1=顶点数]
    Mesh_Materials_Number,             // 网格材质槽索引数 [int0]
    Mesh_LOD_Section_Number,           // LOD Section 数 [int0=LOD索引, int1=Section数]
    Mesh_LOD_Section_Vertex_Number,    // Section 顶点数 [int0=LOD, int1=Section, int2=顶点数]
    Mesh_LOD_Section_Triangle_Number,  // Section 三角形数
    Mesh_LOD_Section_Material_Name,    // Section 材质名
    Mesh_LOD_Section_Material_Index,   // Section 材质索引
    Mesh_LOD_Section_Material_Imported_Name, // Section 导入材质名
    Mesh_LOD_Vertex_Position,          // 顶点位置 [int0=LOD, int1=顶点, float0-2=XYZ]
    Mesh_LOD_Vertex_Normal,            // 顶点法线
    LOD_UV_Channel_Number,             // UV 通道数 [int0=LOD, int1=通道数]
    Bone_Number,                       // 骨骼数量 [int0]
    Bone_Position,                     // 骨骼位置 [int0=索引, float0-2=XYZ, float3=容差]
    Animation_Frame_Number,            // 动画帧数 [int0]
    Animation_Length,                  // 动画长度 [float0]
    Animation_CustomCurve_KeyValue,    // 自定义曲线关键帧值
    Animation_CustomCurve_KeyArriveTangent,       // 到达切线值
    Animation_CustomCurve_KeyLeaveTangent,        // 离开切线值
    Skin_By_Bone_Vertex_Number,        // 按骨骼蒙皮的顶点数
    Animation_CustomCurve_KeyArriveTangentWeight,  // 到达切线权重
    Animation_CustomCurve_KeyLeaveTangentWeight,   // 离开切线权重
};

// 测试计划对象
UCLASS()
class UFbxTestPlan : public UObject
{
    UPROPERTY(EditAnywhere) FString TestPlanName;                       // 计划名称
    UPROPERTY(EditAnywhere) TEnumAsByte<EFBXTestPlanActionType> Action; // 执行动作
    UPROPERTY(EditAnywhere) int32 LodIndex;                             // LOD 索引（AddLOD/ReimportLOD 时使用）
    UPROPERTY(EditAnywhere) bool bDeleteFolderAssets;                   // 测试后删除导入文件夹中的资产
    UPROPERTY(EditAnywhere) TArray<FFbxTestPlanExpectedResult> ExpectedResult; // 预期结果列表
    UPROPERTY(EditAnywhere, Transient, Instanced) TObjectPtr<UFbxImportUI> ImportUI; // FBX 导入选项
};
```

### JSON 序列化 API

```cpp
// 来源: Engine/Source/Editor/UnrealEd/Public/Tests/FbxAutomationCommon.h

namespace FbxAutomationTestsAPI
{
    // 从 JSON 文件读取测试计划
    UNREALED_API void ReadFbxOptions(
        const FString& FileOptionAndResult,
        TArray<UFbxTestPlan*>& TestPlanArray
    );

    // 将测试计划写入 JSON 文件
    UNREALED_API void WriteFbxOptions(
        const FString& Filename,
        TArray<UFbxTestPlan*>& TestPlanArray
    );
}
```

### 基本用法：程序化创建测试计划

```cpp
#include "Tests/FbxAutomationCommon.h"
#include "Factories/FbxImportUI.h"

// 创建一个测试计划
UFbxTestPlan* TestPlan = NewObject<UFbxTestPlan>();
TestPlan->AddToRoot();
TestPlan->TestPlanName = TEXT("BasicStaticMeshImport");
TestPlan->Action = EFBXTestPlanActionType::Import;
TestPlan->LodIndex = 0;
TestPlan->bDeleteFolderAssets = true;

// 配置 FBX 导入选项
TestPlan->ImportUI = NewObject<UFbxImportUI>();
TestPlan->ImportUI->AddToRoot();
TestPlan->ImportUI->bImportAsSkeletal = false;
TestPlan->ImportUI->MeshTypeToImport = FBXIT_StaticMesh;

// 添加预期结果：应创建 1 个静态网格
FFbxTestPlanExpectedResult MeshCountResult;
MeshCountResult.ExpectedPresetsType = EFBXExpectedResultPreset::Created_Staticmesh_Number;
MeshCountResult.ExpectedPresetsDataInteger.Add(1);
TestPlan->ExpectedResult.Add(MeshCountResult);

// 添加预期结果：总顶点数为 1024
FFbxTestPlanExpectedResult VertexResult;
VertexResult.ExpectedPresetsType = EFBXExpectedResultPreset::Vertex_Number;
VertexResult.ExpectedPresetsDataInteger.Add(1024);
TestPlan->ExpectedResult.Add(VertexResult);

// 保存为 JSON
TArray<UFbxTestPlan*> AllPlans;
AllPlans.Add(TestPlan);
FbxAutomationTestsAPI::WriteFbxOptions(TEXT("/Path/to/TestModel.json"), AllPlans);
```

### 进阶用法：多步骤测试计划

一个 JSON 文件可以包含多个测试计划，按顺序执行。例如先导入、再重新导入、再添加 LOD：

```cpp
#include "Tests/FbxAutomationCommon.h"
#include "Factories/FbxImportUI.h"

TArray<UFbxTestPlan*> AllPlans;

// 步骤 1：初始导入
UFbxTestPlan* ImportPlan = NewObject<UFbxTestPlan>();
ImportPlan->AddToRoot();
ImportPlan->TestPlanName = TEXT("InitialImport");
ImportPlan->Action = EFBXTestPlanActionType::Import;
ImportPlan->ImportUI = NewObject<UFbxImportUI>();
ImportPlan->ImportUI->AddToRoot();
ImportPlan->ImportUI->bImportAsSkeletal = false;
// ... 设置导入选项 ...

FFbxTestPlanExpectedResult MeshCount;
MeshCount.ExpectedPresetsType = EFBXExpectedResultPreset::Created_Staticmesh_Number;
MeshCount.ExpectedPresetsDataInteger.Add(1);
ImportPlan->ExpectedResult.Add(MeshCount);

AllPlans.Add(ImportPlan);

// 步骤 2：重新导入（测试 Re-import 管线）
UFbxTestPlan* ReimportPlan = NewObject<UFbxTestPlan>();
ReimportPlan->AddToRoot();
ReimportPlan->TestPlanName = TEXT("ReimportTest");
ReimportPlan->Action = EFBXTestPlanActionType::Reimport;
ReimportPlan->ImportUI = NewObject<UFbxTestPlan>()->ImportUI; // 可复用或调整选项
ReimportPlan->ImportUI->AddToRoot();
// ... 设置重新导入选项 ...

AllPlans.Add(ReimportPlan);

// 步骤 3：添加 LOD（需要 _lod01.fbx 文件存在）
UFbxTestPlan* LODPlan = NewObject<UFbxTestPlan>();
LODPlan->AddToRoot();
LODPlan->TestPlanName = TEXT("AddLOD1");
LODPlan->Action = EFBXTestPlanActionType::AddLOD;
LODPlan->LodIndex = 1;
LODPlan->ImportUI = NewObject<UFbxImportUI>();
LODPlan->ImportUI->AddToRoot();
// ... 设置 LOD 导入选项 ...

FFbxTestPlanExpectedResult LodCount;
LodCount.ExpectedPresetsType = EFBXExpectedResultPreset::Lod_Number;
LodCount.ExpectedPresetsDataInteger.Add(2); // 期望有 2 个 LOD
LODPlan->ExpectedResult.Add(LodCount);

AllPlans.Add(LODPlan);

// 保存
FbxAutomationTestsAPI::WriteFbxOptions(TEXT("/Path/to/MyModel.json"), AllPlans);
```

## 编辑器 UI 用法

插件启用后，在编辑器主菜单 **Window → Developer Tools → FBX Test Builder** 打开工具窗口（注册在 Automation Tools 分类下）。

### 界面布局

窗口从上到下分为：

1. **Select a fbx file** — 下拉按钮，从配置的测试目录中选择 FBX 文件
2. **Select a test plan** — 下拉按钮，选择已有测试计划或 "Create new plan"
3. **操作按钮** — "Save JSON"（保存）和 "Delete CurrentPlan"（删除当前计划）
4. **Details 面板** — 显示当前选中的 `UFbxTestPlan` 的属性编辑器

### 配置测试目录

插件通过 `GEngineIni` 中的配置项查找 FBX 文件：

```ini
[AutomationTesting.FbxImport]
FbxImportEditorTestPath=Path/To/Your/Fbx/Test/Files
```

同样的路径也用于 `Editor.Import.Fbx` 自动化测试。

### 文件过滤规则

工具会自动过滤以下文件：
- LOD 变体文件：`_lod01`、`_lod02` 等（只保留 `_lod00` 或无 LOD 后缀的文件作为基础导入文件）
- 备用蒙皮文件：以 `_alt` 结尾的文件

### JSON 文件规则

- JSON 文件与 FBX 文件同名，只是扩展名从 `.fbx` 变为 `.json`
- 例如：`MyModel.fbx` → `MyModel.json`
- 如果 JSON 文件是只读的，工具会以只读模式显示，不能修改

## Demo 示例

此插件是纯编辑器工具，不需要编写代码来使用。典型工作流：

1. 启用插件
2. 配置 `FbxImportEditorTestPath` 指向你的测试 FBX 目录
3. 打开 FBX Test Builder 窗口
4. 选择 FBX 文件 → 创建新计划 → 配置导入选项和预期结果 → 保存
5. 在 Session Frontend 的 Automation 标签中运行 `Editor.Import.Fbx` 测试

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `InputCore` | 输入系统基础 |
| `Slate` | UI 框架 |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器框架 |
| `PropertyEditor` | Details 面板属性编辑器 |
| `LevelEditor` | 关卡编辑器集成 |
| `WorkspaceMenuStructure` | 工作区菜单分类（将标签注册到 Automation Tools） |
| `EditorFramework` | 编辑器框架（仅编辑器构建时） |
| `SlateCore` | Slate 核心样式（仅编辑器构建时） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da71ab9` | Another batch iwyu updates to reduce number of includes used in files | IWYU（Include What You Use）重构，非功能性修改 |
| 2022-11-07 | `0a10c21ff628` | Update Release-Engine-Staging from UE5/Main | 引擎版本合并，非针对性更新 |
| 2022-05-06 | `07436403cc84` | Replacing legacy EditorStyle calls with AppStyle | UE5 API 迁移（`EditorStyle` → `AppStyle`），非功能性修改 |

### 维护评价

- **创建时间**：2016 年 9 月，已超过 9 年
- **最近更新**：最后一次实质性功能更新远早于 2022 年；近期更新全部是代码维护性修改（IWYU、API 迁移、版本合并）
- **维护状态**：**可能废弃** — 超过 1 年没有实质性功能更新，且 UE5 正在推广使用 Interchange 框架替代传统 FBX 导入管线（测试代码中已显式禁用 Interchange：`CVarInterchangeFbx->Set(false)`）
- **已知限制**：
  - 插件自身代码中有一些已注释掉的功能（如 Detail 自定义布局 `UFbxAutomationBuilderView`），说明曾经计划扩展但未完成
  - 不支持在 Commandlet 模式下运行（测试需要 Slate UI 路由）
- **推荐程度**：如果你需要为 FBX 导入创建自动化测试，这个工具仍然可用。但考虑到 FBX 导入管线正在向 Interchange 迁移，长期来看此工具的适用范围可能会缩小。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/FbxAutomationTestBuilder)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/EditorTests/Source/EditorTests/Private/UnrealEd/FbxAutomationTests.cpp) — `FFbxImportAssetsAutomationTest`，实际执行测试计划的自动化测试
- [FbxAutomationCommon.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Editor/UnrealEd/Public/Tests/FbxAutomationCommon.h) — 测试计划数据结构和序列化 API 的定义
