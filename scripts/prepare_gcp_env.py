import os

def main():
    env_file = 'backend/.env'
    output_file = 'env.yaml'
    
    if not os.path.exists(env_file):
        print(f"❌ Error: {env_file} not found.")
        exit(1)
        
    print(f"Reading {env_file}...")
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    # Overrides for Production
    env_vars['FLASK_ENV'] = 'production'
    env_vars['FLASK_DEBUG'] = 'False'
    
    # PORT is reserved by Cloud Run, remove it if present in .env
    if 'PORT' in env_vars:
        del env_vars['PORT']
    
    # Write to YAML
    print(f"Writing {output_file}...")
    with open(output_file, 'w') as f:
        for key, value in env_vars.items():
            # Force all values to be strings by quoting them
            # This fixes the "Environment variable values must be strings" error
            f.write(f'{key}: "{value}"\n')
            
    print("✅ env.yaml created successfully.")

if __name__ == '__main__':
    main()
