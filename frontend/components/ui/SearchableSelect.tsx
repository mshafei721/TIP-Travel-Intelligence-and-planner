'use client';

import Select, { StylesConfig, GroupBase } from 'react-select';
import { useTheme } from 'next-themes';

export interface SelectOption {
  value: string;
  label: string;
}

interface SearchableSelectProps {
  value: SelectOption | null;
  onChange: (option: SelectOption | null) => void;
  options: SelectOption[];
  placeholder?: string;
  isDisabled?: boolean;
  isLoading?: boolean;
  isClearable?: boolean;
  noOptionsMessage?: string;
  className?: string;
  menuPosition?: 'fixed' | 'absolute';
}

export function SearchableSelect({
  value,
  onChange,
  options,
  placeholder = 'Select...',
  isDisabled = false,
  isLoading = false,
  isClearable = true,
  noOptionsMessage = 'No options found',
  className,
  menuPosition = 'fixed',
}: SearchableSelectProps) {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  // Portal target for the menu - use document.body on client-side
  // This is safe because 'use client' ensures this only runs on the client
  const menuPortalTarget = typeof window !== 'undefined' ? document.body : null;

  const customStyles: StylesConfig<SelectOption, false, GroupBase<SelectOption>> = {
    control: (base, state) => ({
      ...base,
      backgroundColor: isDark ? 'rgb(15 23 42)' : 'white', // slate-900 : white
      borderColor: state.isFocused
        ? 'rgb(59 130 246)' // blue-500
        : isDark
          ? 'rgb(51 65 85)' // slate-700
          : 'rgb(203 213 225)', // slate-300
      borderRadius: '0.5rem',
      padding: '0.25rem',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(59, 130, 246, 0.3)' : 'none',
      '&:hover': {
        borderColor: 'rgb(59 130 246)',
      },
      minHeight: '46px',
    }),
    menu: (base) => ({
      ...base,
      backgroundColor: isDark ? 'rgb(15 23 42)' : 'white',
      borderRadius: '0.5rem',
      border: isDark ? '1px solid rgb(51 65 85)' : '1px solid rgb(203 213 225)',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
      zIndex: 9999,
    }),
    menuPortal: (base) => ({
      ...base,
      zIndex: 9999,
    }),
    menuList: (base) => ({
      ...base,
      maxHeight: '200px',
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected
        ? 'rgb(59 130 246)' // blue-500
        : state.isFocused
          ? isDark
            ? 'rgb(30 41 59)' // slate-800
            : 'rgb(241 245 249)' // slate-100
          : 'transparent',
      color: state.isSelected
        ? 'white'
        : isDark
          ? 'rgb(226 232 240)' // slate-200
          : 'rgb(15 23 42)', // slate-900
      cursor: 'pointer',
      '&:active': {
        backgroundColor: 'rgb(59 130 246)',
      },
    }),
    singleValue: (base) => ({
      ...base,
      color: isDark ? 'rgb(241 245 249)' : 'rgb(15 23 42)', // slate-100 : slate-900
    }),
    input: (base) => ({
      ...base,
      color: isDark ? 'rgb(241 245 249)' : 'rgb(15 23 42)',
    }),
    placeholder: (base) => ({
      ...base,
      color: isDark ? 'rgb(100 116 139)' : 'rgb(148 163 184)', // slate-500 : slate-400
    }),
    indicatorSeparator: () => ({
      display: 'none',
    }),
    dropdownIndicator: (base) => ({
      ...base,
      color: isDark ? 'rgb(100 116 139)' : 'rgb(148 163 184)',
      '&:hover': {
        color: isDark ? 'rgb(148 163 184)' : 'rgb(100 116 139)',
      },
    }),
    clearIndicator: (base) => ({
      ...base,
      color: isDark ? 'rgb(100 116 139)' : 'rgb(148 163 184)',
      '&:hover': {
        color: 'rgb(239 68 68)', // red-500
      },
    }),
    noOptionsMessage: (base) => ({
      ...base,
      color: isDark ? 'rgb(148 163 184)' : 'rgb(100 116 139)',
    }),
    loadingMessage: (base) => ({
      ...base,
      color: isDark ? 'rgb(148 163 184)' : 'rgb(100 116 139)',
    }),
  };

  return (
    <Select<SelectOption, false>
      value={value}
      onChange={onChange}
      options={options}
      placeholder={placeholder}
      isDisabled={isDisabled}
      isLoading={isLoading}
      isClearable={isClearable}
      isSearchable
      styles={customStyles}
      noOptionsMessage={() => noOptionsMessage}
      className={className}
      classNamePrefix="react-select"
      menuPortalTarget={menuPortalTarget}
      menuPosition={menuPosition}
    />
  );
}
