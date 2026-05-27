# Database Support

> Abstract Database Support

| 属性 | 值 |
|---|---|
| 中文名 | 数据库抽象层 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatabaseSupport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/DatabaseSupport) | |

## 用途

DatabaseSupport 是一个**纯抽象接口层**，本身不提供任何数据库连接实现。它定义了数据库操作的基础接口：连接管理（`FDataBaseConnection`）和结果集遍历（`FDataBaseRecordSet`）。

这个插件的存在意义是为其他具体数据库实现（如 SQLiteSupport）提供统一的抽象层。通过继承这些基类，不同的数据库后端可以提供一致的 API，使上层代码无需关心底层数据库类型。

该插件默认隐藏（Hidden=true）且不默认启用（EnabledByDefault=false），说明它是一个底层基础设施模块，不建议直接使用，而是被其他数据库插件间接依赖。

## 使用场景

- 你需要为 UE5 项目集成自定义数据库后端 → 继承 `FDataBaseConnection` 和 `FDataBaseRecordSet`
- 你在开发跨平台数据库抽象层 → 使用这些接口保证 API 一致性
- 你使用 SQLiteSupport 等官方数据库插件 → 它们在底层依赖本插件的接口定义

## 蓝图用法

本插件没有暴露任何蓝图接口。所有 API 均为纯 C++ 抽象类，不包含 `BlueprintCallable` 或 `BlueprintReadWrite` 标记。

## C++ 用法

### 头文件引入

```cpp
#include "Database.h"
#include "DatabaseSupport.h"
```

### 基本用法

本插件的核心是两个抽象基类和一个辅助结构体：

**列信息结构体 `FDatabaseColumnInfo`**：

```cpp
// 描述数据库查询结果中某列的元信息
FDatabaseColumnInfo ColumnInfo;
ColumnInfo.ColumnName = TEXT("UserName");
ColumnInfo.DataType = EDataBaseUnrealTypes::DBT_STRING;
```

**结果集遍历 `FDataBaseRecordSet`**：

```cpp
// 假设 RecordSet 是某个具体数据库实现返回的结果集
void ProcessResults(FDataBaseRecordSet* RecordSet)
{
    if (RecordSet->HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("Database error: %s"), *RecordSet->GetErrorMessage());
        return;
    }

    // 使用内置迭代器遍历所有记录
    for (FDataBaseRecordSet::TIterator It(RecordSet); It; ++It)
    {
        FString Name = It->GetString(TEXT("UserName"));
        int32 Age = It->GetInt(TEXT("Age"));
        float Score = It->GetFloat(TEXT("Score"));
        int64 ID = It->GetBigInt(TEXT("ID"));
    }

    // 或者手动控制遍历
    int32 Count = RecordSet->GetRecordCount();

    // 获取列元信息（动态获取可用列名和类型）
    TArray<FDatabaseColumnInfo> Columns = RecordSet->GetColumnNames();
    for (const FDatabaseColumnInfo& Col : Columns)
    {
        UE_LOG(LogTemp, Log, TEXT("Column: %s, Type: %d"), *Col.ColumnName, (int32)Col.DataType);
    }
}
```

**数据库连接 `FDataBaseConnection`**：

```cpp
// 使用具体实现创建连接
FDataBaseConnection* Connection = CreateSomeDatabaseConnection(); // 由子类提供

// 打开连接
bool bSuccess = Connection->Open(
    TEXT("ConnectionString"),           // 连接字符串
    TEXT("127.0.0.1"),                  // 远程连接 IP
    TEXT("OverrideConnectionString")    // 覆盖连接字符串
);

// 执行不返回结果的命令（如 INSERT、UPDATE）
Connection->Execute(TEXT("INSERT INTO Users (Name, Age) VALUES ('Alice', 30)"));

// 执行返回结果集的命令（如 SELECT）
FDataBaseRecordSet* RecordSet = nullptr;
if (Connection->Execute(TEXT("SELECT * FROM Users WHERE Age > 18"), RecordSet))
{
    // 使用 RecordSet...
    // 调用者负责删除 RecordSet
    delete RecordSet;
}

// 或使用 TUniquePtr 自动管理生命周期
TUniquePtr<FDataBaseRecordSet> SafeRecordSet;
Connection->Execute(TEXT("SELECT * FROM Users"), SafeRecordSet);

// 关闭连接
Connection->Close();
```

### 进阶用法

**继承实现自定义数据库后端**：

```cpp
// 以继承方式实现具体数据库连接
class FMyDatabaseConnection : public FDataBaseConnection
{
public:
    virtual bool Open(const TCHAR* ConnectionString,
                      const TCHAR* RemoteConnectionIP,
                      const TCHAR* RemoteConnectionStringOverride) override
    {
        // 实现实际的数据库连接逻辑
        return true;
    }

    virtual void Close() override
    {
        // 关闭实际连接
    }

    virtual bool Execute(const TCHAR* CommandString, FDataBaseRecordSet*& RecordSet) override
    {
        // 执行 SQL 并返回自定义结果集
        RecordSet = new FMyDatabaseRecordSet();
        return true;
    }
};

// 继承实现自定义结果集
class FMyDatabaseRecordSet : public FDataBaseRecordSet
{
public:
    virtual FString GetString(const TCHAR* Column) const override { return TEXT("value"); }
    virtual int32 GetInt(const TCHAR* Column) const override { return 42; }
    virtual float GetFloat(const TCHAR* Column) const override { return 3.14f; }
    virtual int64 GetBigInt(const TCHAR* Column) const override { return 123456789LL; }
    virtual TArray<FDatabaseColumnInfo> GetColumnNames() const override
    {
        TArray<FDatabaseColumnInfo> Columns;
        FDatabaseColumnInfo Info;
        Info.ColumnName = TEXT("Name");
        Info.DataType = EDataBaseUnrealTypes::DBT_STRING;
        Columns.Add(Info);
        return Columns;
    }
    virtual int32 GetRecordCount() const override { return 10; }
    virtual void MoveToFirst() override { /* 移动游标到首行 */ }
    virtual void MoveToNext() override { /* 移动游标到下一行 */ }
    virtual bool IsAtEnd() const override { return false; }
    virtual bool HasError() const override { return false; }
};
```

## Demo 示例

```cpp
// MyDatabaseExample.h
#pragma once

#include "Database.h"

// 自定义数据库连接实现（演示用，无实际后端）
class FExampleConnection : public FDataBaseConnection
{
public:
    virtual bool Open(const TCHAR* ConnectionString,
                      const TCHAR* RemoteConnectionIP,
                      const TCHAR* RemoteConnectionStringOverride) override;
    virtual void Close() override;
    virtual bool Execute(const TCHAR* CommandString) override;
    virtual bool Execute(const TCHAR* CommandString, FDataBaseRecordSet*& RecordSet) override;
};

// 自定义结果集实现
class FExampleRecordSet : public FDataBaseRecordSet
{
    TArray<TMap<FString, FString>> Rows;
    int32 CurrentIndex = 0;

public:
    FExampleRecordSet();
    virtual int32 GetRecordCount() const override;
    virtual FString GetString(const TCHAR* Column) const override;
    virtual int32 GetInt(const TCHAR* Column) const override;
    virtual TArray<FDatabaseColumnInfo> GetColumnNames() const override;

protected:
    virtual void MoveToFirst() override;
    virtual void MoveToNext() override;
    virtual bool IsAtEnd() const override;
};
```

```cpp
// MyDatabaseExample.cpp
#include "MyDatabaseExample.h"

bool FExampleConnection::Open(const TCHAR* ConnectionString,
                               const TCHAR* RemoteConnectionIP,
                               const TCHAR* RemoteConnectionStringOverride)
{
    UE_LOG(LogTemp, Log, TEXT("Connection opened with: %s"), ConnectionString);
    return true;
}

void FExampleConnection::Close()
{
    UE_LOG(LogTemp, Log, TEXT("Connection closed"));
}

bool FExampleConnection::Execute(const TCHAR* CommandString)
{
    UE_LOG(LogTemp, Log, TEXT("Execute: %s"), CommandString);
    return true;
}

bool FExampleConnection::Execute(const TCHAR* CommandString, FDataBaseRecordSet*& RecordSet)
{
    RecordSet = new FExampleRecordSet();
    return true;
}

FExampleRecordSet::FExampleRecordSet()
{
    // 模拟数据
    TMap<FString, FString> Row1;
    Row1.Add(TEXT("Name"), TEXT("Alice"));
    Row1.Add(TEXT("Age"), TEXT("30"));
    Rows.Add(Row1);

    TMap<FString, FString> Row2;
    Row2.Add(TEXT("Name"), TEXT("Bob"));
    Row2.Add(TEXT("Age"), TEXT("25"));
    Rows.Add(Row2);
}

int32 FExampleRecordSet::GetRecordCount() const { return Rows.Num(); }

FString FExampleRecordSet::GetString(const TCHAR* Column) const
{
    if (Rows.IsValidIndex(CurrentIndex))
    {
        const FString* Val = Rows[CurrentIndex].Find(Column);
        return Val ? *Val : FString();
    }
    return FString();
}

int32 FExampleRecordSet::GetInt(const TCHAR* Column) const
{
    const FString Str = GetString(Column);
    return FCString::Atoi(*Str);
}

TArray<FDatabaseColumnInfo> FExampleRecordSet::GetColumnNames() const
{
    TArray<FDatabaseColumnInfo> Columns;
    if (Rows.Num() > 0)
    {
        for (const auto& Pair : Rows[0])
        {
            FDatabaseColumnInfo Info;
            Info.ColumnName = Pair.Key;
            Info.DataType = EDataBaseUnrealTypes::DBT_STRING;
            Columns.Add(Info);
        }
    }
    return Columns;
}

void FExampleRecordSet::MoveToFirst() { CurrentIndex = 0; }
void FExampleRecordSet::MoveToNext() { CurrentIndex++; }
bool FExampleRecordSet::IsAtEnd() const { return CurrentIndex >= Rows.Num(); }
```

## 模块依赖

本插件的 Build.cs 未提供，但基于源码分析，其依赖极为简单。

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-31 | `c8c0f285` | PR #12093: add error detection for SQLiteSupport | 为 SQLiteSupport 添加错误检测，涉及本插件接口变更 |
| 2025-06-13 | `185bf170` | Replace some usages of FORCEINLINE with inline in Engine modules. | 将 FORCEINLINE 替换为 inline，纯代码风格调整 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议 |
| 2019-12-27 | `360d078c` | Second batch of remaining Engine copyright updates. | 批量更新引擎版权信息 |
| 2019-01-10 | `57c677da` | Copying //UE4/Dev-Enterprise@4705006 to Dev-Main | 从 Enterprise 分支复制到 Main 分支，插件初始提交 |

### 维护评价

本插件属于**稳定基础设施**，代码量极小（3 个文件），功能自 2019 年创建以来基本未变。

- **创建时间**：2019 年，来自 Epic 的 Enterprise 分支
- **更新频率**：非常低，6 年间仅有 5 次提交，且多数为全局性的代码风格或版权更新
- **功能性更新**：2025-10 的最近一次提交是为 SQLiteSupport 添加错误检测，表明该接口仍在被下游使用
- **状态**：隐藏且不默认启用，作为 SQLiteSupport 等插件的底层依赖存在
- **推荐使用**：**不推荐直接使用**。除非你在开发自定义数据库后端，否则应直接使用 SQLiteSupport 等具体实现插件。如果你需要为项目集成非标准数据库，可以继承这些抽象类。

⚠️ 该插件标记为 Hidden，API 稳定性无官方保证，可能在引擎大版本更新时发生变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/DatabaseSupport)
- [官方文档]()（无）
- [测试用例]()（无测试文件）