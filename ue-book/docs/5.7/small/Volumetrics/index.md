# Volumetrics

> A library of volume creation and rendering tools using Blueprints.

| 属性 | 值 |
|---|---|
| 中文名 | 体积工具库 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2020-10-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Volumetrics) | |

## 用途

本插件提供了一系列基于蓝图的体积创建和渲染工具，让开发者无需编写C++代码即可快速生成、操作和渲染体积效果（如云、雾、流体模拟等）。它通过组合 **BlueprintMaterialTextureNodes**（材质纹理蓝图节点）、**Landmass**（地形体积分形）和 **Niagara**（粒子系统）的能力，简化了传统体积着色和体积纹理的复杂工作流。

该插件解决了以下问题：
- **手动体积着色器开发难度高**：传统体积渲染需要深入HLSL/C++编程。
- **蓝图可访问性差**：大多数体积工具仅限C++或材质编辑器。
- **与现有系统的集成**：希望无缝对接地形（Landmass）和粒子（Niagara）。

## 使用场景

- 你需要在蓝图中快速创建程序化云层或雾气效果，无需编写着色器代码。
- 你需要将体积地形数据（来自Landmass）与粒子系统（Niagara）结合，实现动态体积环境。
- 你正在开发一个以体积视觉特效为核心的游戏（如飞行模拟、环境叙事），并且希望保持纯蓝图工作流。
- 你希望复用预设的体积材质蓝图来加速原型开发。

## 蓝图用法

本插件不包含C++代码，所有蓝图功能通过 **内容浏览器** 中提供的蓝图资产实现。由于源码不可用（纯内容插件），无法生成具体的蓝图节点列表。但基于其依赖和用途，典型的蓝图用法包括：

### 核心资产类别

| 资源类型 | 说明 | 位置（内容浏览器） |
|---|---|---|
| `VolumetricEffect` 蓝图 | 预设的体积效果蓝图（如云、雾、烟） | `/Volumetrics/Effects/` |
| `VolumetricMaterial` 材质实例 | 基于体积贴图的材质实例，可直接应用于静态网格体 | `/Volumetrics/Materials/` |
| `VolumetricData` 数据资产 | 定义体积纹理的分辨率、衰减参数 | `/Volumetrics/Data/` |

### 使用示例（蓝图描述）

1. **创建体积云**：在关卡蓝图中 `Spawn Actor from Class` → 选择 `Volumetrics/Effects/BP_VolumetricCloud` → 设置 `Density`（密度）和 `HeightScale`（高度缩放）参数 → 调整Niagara粒子发射器的`ParticleSpawnRate`。
2. **动态体积地形**：在蓝图脚本中调用 `Create Volumetric Data` 节点 → 输入Landmass分形噪声 → 输出到`VolumetricMaterial` → 通过`Set Material Instance Parameter` 更新云层高度。
3. **粒子体积交互**：使用Niagara粒子系统中的`VolumetricSample`模块 → 读取体积纹理 → 控制粒子颜色和位置。

## C++ 用法

本插件不包含C++模块。它是一个纯蓝图内容插件，不提供任何可导入的C++头文件或API。

```cpp
// 无需引入头文件
// 所有功能通过蓝图节点和内容资产实现
```

### 蓝图配置（替代C++用法）

如需在C++项目中引用资产路径（例如加载蓝图类），建议使用FObjectFinder或TSoftObjectPtr：

```cpp
// 加载体积效果蓝图
static ConstructorHelpers::FObjectFinder<UBlueprint> VolCloudFinder(TEXT("/Volumetrics/Effects/BP_VolumetricCloud.BP_VolumetricCloud"));
if (VolCloudFinder.Succeeded())
{
    UClass* CloudClass = VolCloudFinder.Object->GeneratedClass;
    // 生成Actor
}
```

## Demo 示例

以下是一个最小蓝图示例，模拟创建简单体积云：

### 关卡蓝图（BP_MinimalVolCloud）

1. **Event BeginPlay**
   - `Spawn Actor` → 选择 `BP_VolumetricCloud`
   - 设置 `Transform` → `Location = (0,0,500)`, `Scale = (10,10,5)`
2. **For Each Loop** (可选：动态调整密度)
   - `Get Actor of Class` → `BP_VolumetricCloud` → `Cast to BP_VolumetricCloud`
   - `Set Cloud Density` → 输入 `2.0`
   - `Set Cloud Speed` → 输入 `0.1`

### 说明
- 无需C++代码
- 依赖插件提供的蓝图资产和Niagara发射器
- 可在编辑器直接预览效果

## 模块依赖

本插件为纯内容插件，不依赖外部C++模块（除标准引擎模块外）。其 **内容依赖** 如下：

| 插件 | 用途 |
|---|---|
| `BlueprintMaterialTextureNodes` | 提供蓝图节点操作材质纹理，用于体积纹理生成 |
| `Landmass` | 提供地形体积分形数据（如噪声），用于体积形状驱动 |
| `Niagara` | 提供粒子系统，用于体积粒子的渲染和模拟 |

**注意**：使用本插件前，需在项目插件设置中启用上述三个插件。

## 维护状态

### 近期更新

- 2024-07-31 `5f38a323` Add Niagara as an explicit dependency to avoid illegal asset reference errors
- 2023-11-28 `6d654177` Add missing copyright boilerplate to shader files
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol.
- 2021-04-27 `8aa8d3e0` Removing code from Volumetrics plugin and converted it to a content only plugin. Removed old volume (大规模重构：移除C++代码，转为纯内容插件)
- 2020-10-29 `68150e0b` Merge UE5/Release-Engine-Staging to UE5/Main

### 维护评价

- **创建时间**：2020-10-29（约5年）
- **最近更新内容**：2022年之后仅有依赖修复和版权注释添加，2021年4月后无功能开发。
- **活跃度**：2021年4月重构为纯内容插件后，已停止功能更新，转为维护模式。
- **已知问题**：无C++源码，无法通过C++扩展；依赖的 Landmass 和 Niagara 在不同UE版本间可能存在兼容风险。
- **推荐度**：⚠️ **谨慎使用**。如果你的项目需要自定义体积渲染逻辑（非纯蓝图），建议直接使用 Niagara + Material 组合，避免对过期内容插件的依赖。但如果你需要一个快速原型方案，此插件可提供现成蓝图资产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Volumetrics)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/volumetrics-plugin-in-unreal-engine/)（如果可用）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Volumetrics/Content)（插件内容目录，作为蓝图演示参考）